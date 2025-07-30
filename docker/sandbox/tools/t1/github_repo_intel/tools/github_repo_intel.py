from collections.abc import Generator
from typing import Any, Dict, List, Optional
import requests
import json
import time
from datetime import datetime, timedelta
import re
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GithubRepoIntelTool(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHubRepoIntel-Dify-Plugin"
        }
        self.rate_limit_info = {
            "remaining": 60,
            "reset_time": None,
            "is_authenticated": False
        }

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # Extract parameters
            query = tool_parameters.get("query", "").strip()
            analysis_type = tool_parameters.get("analysis_type", "auto")
            limit = min(int(tool_parameters.get("limit", 10)), 50)

            # Validate query
            if not query:
                yield self.create_text_message("Query parameter is required. Please provide a repository name, search query, or analysis request.")
                return

            # Setup authentication
            github_token = self.runtime.credentials.get("github_token", "")
            if github_token:
                self.headers["Authorization"] = f"Bearer {github_token}"
                self.rate_limit_info["remaining"] = 5000
                self.rate_limit_info["is_authenticated"] = True

            # Check rate limit
            if not self._check_rate_limit():
                yield self.create_text_message("Rate limit exceeded. Please wait before making more requests.")
                return

            # Auto-detect analysis type if not specified
            if analysis_type == "auto":
                analysis_type = self._detect_analysis_type(query)

            # Perform analysis based on type
            if analysis_type == "search":
                result = self._search_repositories(query, limit)
            elif analysis_type == "analyze":
                result = self._analyze_repository(query)
            elif analysis_type == "trending":
                result = self._get_trending_repositories(query, limit)
            elif analysis_type == "compare":
                result = self._compare_repositories(query, limit)
            else:
                result = self._comprehensive_analysis(query, limit)

            # Add metadata
            result["metadata"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "rate_limit_remaining": self.rate_limit_info["remaining"],
                "is_authenticated": self.rate_limit_info["is_authenticated"],
                "tier": "authenticated" if self.rate_limit_info["is_authenticated"] else "free",
                "confidence_score": self._calculate_confidence_score(result),
                "data_freshness": "real_time"
            }

            # Yield results
            yield self.create_text_message(self._format_summary(result))
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")

    def _check_rate_limit(self) -> bool:
        """Check current rate limit status"""
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                core_limit = data.get("resources", {}).get("core", {})
                self.rate_limit_info["remaining"] = core_limit.get("remaining", 0)
                self.rate_limit_info["reset_time"] = core_limit.get("reset")
                return self.rate_limit_info["remaining"] > 0
            return True  # Assume OK if can't check
        except:
            return True  # Assume OK if can't check

    def _detect_analysis_type(self, query: str) -> str:
        """Auto-detect analysis type based on query"""
        query_lower = query.lower()
        
        if "/" in query and " " not in query:
            return "analyze"
        elif any(word in query_lower for word in ["trending", "popular", "latest", "hot"]):
            return "trending"
        elif any(word in query_lower for word in ["compare", "vs", "versus"]):
            return "compare"
        else:
            return "search"

    def _search_repositories(self, query: str, limit: int) -> Dict[str, Any]:
        """Search for repositories"""
        params = {
            "q": query,
            "sort": "best_match",
            "per_page": limit
        }

        response = requests.get(f"{self.base_url}/search/repositories", headers=self.headers, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code}")

        data = response.json()
        
        return {
            "type": "repository_search",
            "query": query,
            "total_count": data.get("total_count", 0),
            "repositories": [
                {
                    "name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "url": repo.get("html_url", ""),
                    "created_at": repo.get("created_at", ""),
                    "updated_at": repo.get("updated_at", ""),
                    "topics": repo.get("topics", []),
                    "license": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                    "open_issues": repo.get("open_issues_count", 0),
                    "size": repo.get("size", 0),
                    "default_branch": repo.get("default_branch", ""),
                    "visibility": repo.get("visibility", ""),
                    "archived": repo.get("archived", False),
                    "disabled": repo.get("disabled", False)
                }
                for repo in data.get("items", [])
            ],
            "insights": self._generate_search_insights(data.get("items", []))
        }

    def _analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """Perform detailed repository analysis"""
        if "/" not in repo_name:
            raise Exception("Repository name must be in format 'owner/repo'")

        owner, repo = repo_name.split("/", 1)
        
        # Get basic repo info
        repo_data = self._get_repository_data(owner, repo)
        if not repo_data:
            raise Exception(f"Repository {repo_name} not found")

        # Get additional data if authenticated
        analysis = {
            "type": "repository_analysis",
            "repository": repo_name,
            "basic_info": repo_data,
            "health_score": None,
            "tech_stack": None,
            "contributor_insights": None
        }

        if self.rate_limit_info["is_authenticated"]:
            # Advanced analysis for authenticated users
            analysis["health_score"] = self._calculate_health_score(owner, repo)
            analysis["tech_stack"] = self._extract_tech_stack_from_repo(owner, repo)
            analysis["contributor_insights"] = self._get_contributor_insights(owner, repo)

        return analysis

    def _get_repository_data(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get basic repository data"""
        response = requests.get(f"{self.base_url}/repos/{owner}/{repo}", headers=self.headers, timeout=10)
        
        if response.status_code != 200:
            return None

        data = response.json()
        
        return {
            "name": data["full_name"],
            "description": data.get("description", ""),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "language": data.get("language", ""),
            "url": data.get("html_url", ""),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "pushed_at": data.get("pushed_at", ""),
            "topics": data.get("topics", []),
            "license": data.get("license", {}).get("name", "") if data.get("license") else "",
            "open_issues": data.get("open_issues_count", 0),
            "size": data.get("size", 0),
            "default_branch": data.get("default_branch", ""),
            "visibility": data.get("visibility", ""),
            "archived": data.get("archived", False),
            "disabled": data.get("disabled", False),
            "has_wiki": data.get("has_wiki", False),
            "has_pages": data.get("has_pages", False),
            "has_downloads": data.get("has_downloads", False),
            "subscribers_count": data.get("subscribers_count", 0),
            "network_count": data.get("network_count", 0)
        }

    def _calculate_health_score(self, owner: str, repo: str) -> Dict[str, Any]:
        """Calculate repository health score"""
        try:
            # Get recent commits
            commits_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits",
                headers=self.headers,
                params={"per_page": 30},
                timeout=10
            )
            
            # Get recent issues
            issues_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": "open", "per_page": 30},
                timeout=10
            )
            
            # Get contributors
            contributors_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contributors",
                headers=self.headers,
                params={"per_page": 30},
                timeout=10
            )

            commits = commits_response.json() if commits_response.status_code == 200 else []
            issues = issues_response.json() if issues_response.status_code == 200 else []
            contributors = contributors_response.json() if contributors_response.status_code == 200 else []

            # Calculate scores
            commit_frequency = len(commits) / 30 if commits else 0
            issue_resolution = 1 - (len(issues) / 100) if issues else 1
            contributor_diversity = min(len(contributors) / 10, 1) if contributors else 0

            health_score = (commit_frequency * 0.4 + issue_resolution * 0.3 + contributor_diversity * 0.3) * 100

            return {
                "overall_score": round(health_score, 1),
                "commit_frequency_score": round(commit_frequency * 100, 1),
                "issue_resolution_score": round(issue_resolution * 100, 1),
                "contributor_diversity_score": round(contributor_diversity * 100, 1),
                "metrics": {
                    "recent_commits": len(commits),
                    "open_issues": len(issues),
                    "active_contributors": len(contributors)
                }
            }
        except:
            return {"overall_score": 0, "error": "Unable to calculate health score"}

    def _extract_tech_stack_from_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Extract technology stack from repository files"""
        tech_stack = {
            "languages": {},
            "tools": []
        }

        try:
            # Get repository languages
            languages_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/languages",
                headers=self.headers,
                timeout=10
            )
            
            if languages_response.status_code == 200:
                tech_stack["languages"] = languages_response.json()

            # Try to get package.json, requirements.txt, etc.
            config_files = ["package.json", "requirements.txt", "Dockerfile", "pom.xml", "build.gradle", "Cargo.toml"]
            
            for file in config_files:
                try:
                    content_response = requests.get(
                        f"{self.base_url}/repos/{owner}/{repo}/contents/{file}",
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        if content_data.get("type") == "file":
                            tech_stack["tools"].append(file)
                except:
                    continue

        except:
            pass

        return tech_stack

    def _get_contributor_insights(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get contributor insights"""
        try:
            contributors_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contributors",
                headers=self.headers,
                params={"per_page": 30},
                timeout=10
            )
            
            if contributors_response.status_code != 200:
                return {"error": "Unable to fetch contributors"}

            contributors = contributors_response.json()
            
            return {
                "total_contributors": len(contributors),
                "top_contributors": [
                    {
                        "username": c["login"],
                        "contributions": c["contributions"],
                        "avatar_url": c["avatar_url"],
                        "profile_url": c["html_url"]
                    }
                    for c in contributors[:10]
                ],
                "contribution_distribution": self._analyze_contribution_distribution(contributors)
            }
        except:
            return {"error": "Unable to analyze contributors"}

    def _analyze_contribution_distribution(self, contributors: List[Dict]) -> Dict[str, Any]:
        """Analyze contribution distribution"""
        if not contributors:
            return {}

        total_contributions = sum(c["contributions"] for c in contributors)
        
        if total_contributions == 0:
            return {}

        # Calculate distribution
        top_contributor_pct = (contributors[0]["contributions"] / total_contributions) * 100
        top_5_pct = (sum(c["contributions"] for c in contributors[:5]) / total_contributions) * 100

        return {
            "top_contributor_percentage": round(top_contributor_pct, 1),
            "top_5_percentage": round(top_5_pct, 1),
            "distribution_type": "concentrated" if top_5_pct > 80 else "distributed"
        }

    def _get_trending_repositories(self, query: str, limit: int) -> Dict[str, Any]:
        """Get trending repositories"""
        # Use search with trending criteria
        search_query = query if query and query.lower() not in ["trending", "popular", "latest", "hot"] else ""
        
        # Add trending criteria
        search_query += " created:>2024-01-01"
        
        return self._search_repositories(search_query, limit)

    def _compare_repositories(self, query: str, limit: int) -> Dict[str, Any]:
        """Compare multiple repositories - optimized version"""
        # Extract repository names from query using simpler regex
        repos = re.findall(r'[\w-]+/[\w-]+', query)
        
        if len(repos) < 2:
            raise Exception("Please provide at least 2 repositories to compare (format: 'repo1 vs repo2')")
        
        comparison = {
            "type": "repository_comparison",
            "repositories": repos[:3],  # Limit to 3 repos for efficiency
            "comparison_data": []
        }
        
        # Fetch data for each repository
        for repo in comparison["repositories"]:
            try:
                owner, repo_name = repo.split("/", 1)
                repo_data = self._get_repository_data(owner, repo_name)
                if repo_data:
                    # Only include essential comparison data
                    comparison["comparison_data"].append({
                        "name": repo_data["name"],
                        "stars": repo_data["stars"],
                        "forks": repo_data["forks"],
                        "language": repo_data["language"],
                        "description": repo_data["description"],
                        "created_at": repo_data["created_at"],
                        "updated_at": repo_data["updated_at"],
                        "open_issues": repo_data["open_issues"],
                        "size": repo_data["size"]
                    })
            except:
                continue
        
        return comparison

    def _comprehensive_analysis(self, query: str, limit: int) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        if "/" in query and " " not in query:
            # Single repository analysis
            return self._analyze_repository(query)
        else:
            # Search and analyze top results
            search_result = self._search_repositories(query, limit)
            
            # Add detailed analysis for top repositories if authenticated
            if self.rate_limit_info["is_authenticated"] and search_result["repositories"]:
                for repo in search_result["repositories"][:3]:  # Analyze top 3
                    try:
                        owner, repo_name = repo["name"].split("/", 1)
                        repo["detailed_analysis"] = {
                            "health_score": self._calculate_health_score(owner, repo_name),
                            "tech_stack": self._extract_tech_stack_from_repo(owner, repo_name)
                        }
                    except:
                        continue
            
            return search_result

    def _generate_search_insights(self, repositories: List[Dict]) -> Dict[str, Any]:
        """Generate insights from search results"""
        if not repositories:
            return {}
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repositories)
        total_forks = sum(repo.get("forks_count", 0) for repo in repositories)
        languages = {}
        
        for repo in repositories:
            lang = repo.get("language", "Unknown")
            languages[lang] = languages.get(lang, 0) + 1
        
        top_language = max(languages.items(), key=lambda x: x[1]) if languages else ("Unknown", 0)
        
        return {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "average_stars": round(total_stars / len(repositories), 1),
            "average_forks": round(total_forks / len(repositories), 1),
            "most_common_language": top_language[0],
            "language_distribution": languages,
            "growth_potential": "high" if total_stars > 10000 else "medium" if total_stars > 1000 else "low"
        }

    def _calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        base_score = 0.8
        
        # Adjust based on data completeness
        if result.get("type") == "repository_analysis":
            if result.get("health_score") and result.get("tech_stack"):
                base_score = 0.95
            elif result.get("basic_info"):
                base_score = 0.85
        
        # Adjust based on authentication
        if self.rate_limit_info["is_authenticated"]:
            base_score += 0.1
        
        return min(base_score, 1.0)

    def _format_summary(self, result: Dict[str, Any]) -> str:
        """Format a human-readable summary of the results"""
        result_type = result.get("type", "analysis")
        
        if result_type == "repository_search":
            repos = result.get("repositories", [])
            total = result.get("total_count", 0)
            insights = result.get("insights", {})
            
            summary = f"Found {total} repositories matching your search.\n\n"
            
            if repos:
                summary += "Top results:\n"
                for i, repo in enumerate(repos[:5], 1):
                    summary += f"{i}. {repo['name']} - {repo['stars']}⭐ {repo['forks']}🍴 ({repo['language']})\n"
                    if repo.get('description'):
                        summary += f"   {repo['description'][:100]}...\n"
                    summary += "\n"
                
                if insights:
                    summary += f"Insights: Most common language is {insights.get('most_common_language', 'Unknown')}, "
                    summary += f"average {insights.get('average_stars', 0)} stars per repository.\n"
            
            return summary
        
        elif result_type == "repository_analysis":
            repo_info = result.get("basic_info", {})
            health_score = result.get("health_score", {})
            
            summary = f"Analysis for {repo_info.get('name', 'Unknown repository')}:\n\n"
            summary += f"Stars: {repo_info.get('stars', 0)} | Forks: {repo_info.get('forks', 0)} | Language: {repo_info.get('language', 'Unknown')}\n"
            summary += f"Created: {repo_info.get('created_at', 'Unknown')} | Last updated: {repo_info.get('updated_at', 'Unknown')}\n\n"
            
            if health_score and health_score.get("overall_score"):
                summary += f"Health Score: {health_score['overall_score']}/100\n"
                summary += f"Commit Frequency: {health_score.get('commit_frequency_score', 0)}/100\n"
                summary += f"Issue Resolution: {health_score.get('issue_resolution_score', 0)}/100\n"
                summary += f"Contributor Diversity: {health_score.get('contributor_diversity_score', 0)}/100\n"
            
            return summary
        
        else:
            return f"Analysis completed. Found {len(result.get('repositories', []))} results."
