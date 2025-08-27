import time
import urllib.parse
from datetime import datetime
from Bio import Entrez
import logging # Added for logging potential parsing issues

logger = logging.getLogger(__name__)

class PubMedAPI:
    """PubMed API interaction class for Dify Plugin"""

    def __init__(self, email, tool="DifyPubMedPlugin", api_key=None):
        """
        Initialize PubMed API interaction class.

        Args:
            email (str): User email address (required by NCBI).
            tool (str): Tool name (required by NCBI).
            api_key (str, optional): NCBI API key for higher request limits.
        """
        if not email:
            raise ValueError("Email address is required for PubMed API access.")

        self.email = email
        self.tool = tool
        self.api_key = api_key

        Entrez.email = self.email
        Entrez.tool = self.tool
        if self.api_key:
            Entrez.api_key = self.api_key
        else:
             if hasattr(Entrez, 'api_key'):
                 delattr(Entrez, 'api_key')

    def search(self, query, max_results=100, sort="relevance", min_date=None, max_date=None):
        """
        Search PubMed articles.
        ... (args documentation) ...
        Raises:
            ValueError: If date format is invalid.
            RuntimeError: If the search fails due to API/network issues.
        """
        date_range_term = ""
        if min_date or max_date:
            min_d = min_date or "1900/01/01"
            max_d = max_date or datetime.now().strftime("%Y/%m/%d")
            try:
                datetime.strptime(min_d, "%Y/%m/%d")
                datetime.strptime(max_d, "%Y/%m/%d")
                date_range_term = f" AND ({min_d}[Date - Publication] : {max_d}[Date - Publication])"
            except ValueError:
                 raise ValueError("Invalid date format. Please use YYYY/MM/DD.")

        full_query = query + date_range_term

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=full_query,
                retmax=str(max_results),
                sort=sort,
                usehistory="y"
            )
            record = Entrez.read(handle)
            handle.close()

            id_list = record.get("IdList", [])
            # count = int(record.get("Count", 0)) # Count isn't strictly needed here

            time.sleep(0.11 if self.api_key else 0.34)

            return id_list

        except Exception as e:
            error_message = f"PubMed search failed. Query: '{query}'. Error: {str(e)}"
            raise RuntimeError(error_message) from e
        
    def fetch_details(self, id_list, batch_size=100):
        """
        Fetch detailed information for a list of PubMed IDs.

        Args:
            id_list (list): List of PubMed IDs (strings).
            batch_size (int): Number of IDs to fetch in each API call.

        Returns:
            list: A list of dictionaries, each containing details for one article.

        Raises:
            RuntimeError: If fetching fails due to API/network issues.
        """
        articles = []
        if not id_list:
            return articles

        logger.info(f"Fetching details for {len(id_list)} PMIDs in batches of {batch_size}")

        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i+batch_size]
            logger.debug(f"Fetching batch {i//batch_size + 1}, IDs: {batch_ids}")
            try:
                # Use Entrez.efetch to get XML data
                handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
                # Parse the XML data
                records = Entrez.read(handle)
                handle.close()

                # Process each article record
                if "PubmedArticle" in records:
                    for record in records["PubmedArticle"]:
                        parsed_article = self._parse_article(record)
                        if parsed_article: # Ensure parsing didn't fail completely
                            articles.append(parsed_article)
                else:
                     logger.warning(f"No 'PubmedArticle' key found in fetched records for batch IDs: {batch_ids}")


                # Adhere to NCBI rate limits
                time.sleep(0.11 if self.api_key else 0.34)

            except Exception as e:
                error_message = f"PubMed fetch details failed for batch IDs {batch_ids}. Error: {str(e)}"
                logger.error(error_message, exc_info=True)
                # Decide whether to continue or fail hard. Let's continue but log.
                # If a complete failure is preferred, raise RuntimeError(error_message) from e here.
                # For now, we return whatever we could fetch before the error.
                # Alternatively, raise the error to stop the whole process:
                raise RuntimeError(error_message) from e


        logger.info(f"Successfully fetched details for {len(articles)} articles.")
        return articles

    def _parse_article(self, record):
        """
        Parse a single PubMed article record from Entrez.read output.
        Based on pubmed-mcp-main/pubmed_api.py _parse_article.
        Returns a dictionary or None if essential info is missing.
        """
        article_data = {}
        try:
            # Essential: PMID
            medline_citation = record.get("MedlineCitation", {})
            pmid = medline_citation.get("PMID")
            if not pmid:
                logger.warning("Skipping record due to missing PMID.")
                return None # Cannot identify article without PMID
            article_data["pmid"] = str(pmid) # Ensure it's a string

            article = medline_citation.get("Article", {})

            # Title
            article_data["title"] = article.get("ArticleTitle", "")

            # Journal Info
            journal = article.get("Journal", {})
            journal_info = {
                "name": journal.get("Title", ""),
                "iso_abbreviation": journal.get("ISOAbbreviation", ""),
                "issn": "", # Initialize
                "volume": journal.get("JournalIssue", {}).get("Volume", ""),
                "issue": journal.get("JournalIssue", {}).get("Issue", ""),
                "pages": article.get("Pagination", {}).get("MedlinePgn", "") # Get pagination if available
            }
            issn_info = journal.get("ISSN")
            if issn_info:
                 journal_info["issn"] = str(issn_info) # Access the string value if ISSN object exists
            article_data["journal"] = journal_info


            # Publication Date (handle potential variations)
            pub_date = {}
            pub_date_section = journal.get("JournalIssue", {}).get("PubDate", {})
            if pub_date_section:
                 # Prioritize structured date fields if available
                if "Year" in pub_date_section:
                    pub_date["year"] = str(pub_date_section["Year"]) # Ensure string
                if "Month" in pub_date_section:
                    pub_date["month"] = str(pub_date_section["Month"])
                if "Day" in pub_date_section:
                    pub_date["day"] = str(pub_date_section["Day"])
                # Fallback for MedlineDate format (e.g., "2023 Jan-Feb")
                if not pub_date and "MedlineDate" in pub_date_section:
                    pub_date["medline_date"] = pub_date_section["MedlineDate"]
            article_data["publication_date"] = pub_date


            # Authors
            authors = []
            author_list = article.get("AuthorList", [])
            # Check if author_list is not None and is iterable
            if author_list and isinstance(author_list, list):
                for author in author_list:
                     # Check author is a dictionary and has required keys
                    if isinstance(author, dict):
                        last_name = author.get("LastName")
                        fore_name = author.get("ForeName")
                        initials = author.get("Initials", "")
                        # Sometimes only CollectiveName is present
                        collective_name = author.get("CollectiveName")

                        author_entry = {}
                        if last_name and fore_name:
                           author_entry = {
                                "last_name": last_name,
                                "fore_name": fore_name,
                                "initials": initials,
                                # Affiliations can be complex, just get the first for simplicity or join them
                                "affiliation": author.get("AffiliationInfo", [{}])[0].get("Affiliation", "") if author.get("AffiliationInfo") else ""
                            }
                        elif collective_name:
                            author_entry = { "collective_name": collective_name }

                        if author_entry: # Add only if we got some name info
                            authors.append(author_entry)

            article_data["authors"] = authors


            # Abstract
            abstract_text = ""
            abstract_section = article.get("Abstract", {}).get("AbstractText", [])
            if abstract_section:
                 parts = []
                 for part in abstract_section:
                     if isinstance(part, str):
                         parts.append(part)
                     # Handle structured abstract parts (like OBJECTIVE:, METHODS:, etc.)
                     elif isinstance(part, dict) and '#text' in part:
                          label = part.attributes.get('Label', '')
                          text = part # Access the text content
                          if label:
                             parts.append(f"{label}: {text}")
                          else:
                             parts.append(str(text)) # Convert StringElement to string
                 abstract_text = "\n".join(parts) # Join parts with newline for readability
            article_data["abstract"] = abstract_text

            # Keywords
            keywords = []
            keyword_lists = medline_citation.get("KeywordList", [])
            if keyword_lists:
                for kw_list in keyword_lists:
                     # kw_list is often a list of StringElements
                     if isinstance(kw_list, list):
                        keywords.extend([str(kw) for kw in kw_list]) # Convert each keyword to string
            article_data["keywords"] = keywords


            # MeSH Headings (Important for indexing)
            mesh_headings = []
            mesh_heading_list = medline_citation.get("MeshHeadingList", [])
            if mesh_heading_list:
                for heading in mesh_heading_list:
                    if isinstance(heading, dict):
                        descriptor = heading.get("DescriptorName")
                        if descriptor:
                            mesh_entry = {"descriptor": str(descriptor)} # Main term
                            qualifiers = []
                            qualifier_list = heading.get("QualifierName", [])
                            if qualifier_list:
                                qualifiers = [str(q) for q in qualifier_list if not q.attributes.get('MajorTopicYN', 'N') == 'Y']
                                major_qualifiers = [str(q) for q in qualifier_list if q.attributes.get('MajorTopicYN', 'N') == 'Y']
                                if qualifiers: mesh_entry["qualifiers"] = qualifiers
                                if major_qualifiers: mesh_entry["major_qualifiers"] = major_qualifiers

                            mesh_headings.append(mesh_entry)
            article_data["mesh_headings"] = mesh_headings


            # DOI and other IDs
            article_data["doi"] = ""
            pubmed_data = record.get("PubmedData", {})
            article_id_list = pubmed_data.get("ArticleIdList", [])
            if article_id_list:
                for article_id in article_id_list:
                    if isinstance(article_id, dict) and article_id.attributes.get("IdType") == "doi":
                        article_data["doi"] = str(article_id) # Get the DOI value
                        break # Usually only one DOI

            # PubMed URL
            article_data["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article_data['pmid']}/"

            return article_data

        except Exception as e:
            # Log parsing errors but don't crash the whole fetch if one article fails
            logger.error(f"Failed to parse article details for PMID (if available) {article_data.get('pmid', 'UNKNOWN')}. Error: {e}", exc_info=True)
            return None # Return None to indicate parsing failure for this record
        
    def advanced_search(self, params: dict):
        """
        Perform an advanced search using specific field tags.

        Args:
            params (dict): Dictionary of search parameters. Expected keys match
                           PubMed field tags (e.g., 'author', 'title', 'journal',
                           'mesh_terms', 'publication_year', 'abstract_keywords').
                           Also accepts 'max_results', 'sort', 'min_date', 'max_date'.

        Returns:
            list: List of PubMed IDs (PMIDs).

        Raises:
            RuntimeError: If the underlying search fails.
            ValueError: If date format is invalid.
        """
        query_parts = []

        # Map input param names to PubMed field tags
        field_map = {
            "author": "Author",
            "title": "Title",
            "journal": "Journal",
            "publication_year": "Publication Date", # Year is handled via date range or direct year tag
            "abstract_keywords": "Abstract",
            "mesh_terms": "MeSH Terms",
            "keywords": "Keyword" # General keywords
            # Add more mappings as needed
        }

        for key, tag in field_map.items():
            if key in params and params[key]:
                 # Handle publication year specifically if needed, otherwise assumes full date range covers it
                 if key == "publication_year":
                     # Could add specific year handling like `params[key][Publication Date]`
                     # But relying on min/max_date is often sufficient and simpler
                     # If only a year is given, construct a date range for that year?
                     # For now, let's assume min/max_date handle year filtering if provided.
                     # Or we could add it explicitly if no min/max_date is set.
                     # Example: query_parts.append(f"{params[key]}[pdat]")
                     pass # Let min/max_date handle this for now
                 else:
                    query_parts.append(f"({params[key]})[{tag}]") # Add parentheses for clarity with AND

        # Combine query parts with AND
        core_query = " AND ".join(query_parts)

        if not core_query:
             # If no specific field searches provided, maybe fall back to a general 'query' param?
             # Or raise an error if advanced search requires at least one field?
             general_query = params.get("general_query", "")
             if not general_query:
                  raise ValueError("Advanced search requires at least one search term in a specific field or a general query.")
             core_query = general_query # Use general query if no specific fields given

        logger.info(f"Constructed advanced search query: {core_query}")

        # Use the existing search method with the constructed query and other params
        return self.search(
            query=core_query,
            max_results=params.get("max_results", 100),
            sort=params.get("sort", "relevance"),
            min_date=params.get("min_date"),
            max_date=params.get("max_date")
        )
