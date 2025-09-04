"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[9483],{69483:function(Gt,qe,z){z.d(qe,{diagram:function(){return jt}});var He=z(80999),s=z(70482),Je=z(17967),A=z(27484),Qe=z(59542),$e=z(10285),et=z(28734),T=z(90166),me=function(){var e=(0,s.eW)(function(x,o,d,f){for(d=d||{},f=x.length;f--;d[x[f]]=o);return d},"o"),i=[6,8,10,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,33,35,36,38,40],a=[1,26],l=[1,27],n=[1,28],h=[1,29],k=[1,30],O=[1,31],B=[1,32],N=[1,33],C=[1,34],L=[1,9],K=[1,10],V=[1,11],R=[1,12],w=[1,13],re=[1,14],se=[1,15],ie=[1,16],ae=[1,19],ne=[1,20],ce=[1,21],le=[1,22],oe=[1,23],y=[1,25],b=[1,35],v={trace:(0,s.eW)(function(){},"trace"),yy:{},symbols_:{error:2,start:3,gantt:4,document:5,EOF:6,line:7,SPACE:8,statement:9,NL:10,weekday:11,weekday_monday:12,weekday_tuesday:13,weekday_wednesday:14,weekday_thursday:15,weekday_friday:16,weekday_saturday:17,weekday_sunday:18,weekend:19,weekend_friday:20,weekend_saturday:21,dateFormat:22,inclusiveEndDates:23,topAxis:24,axisFormat:25,tickInterval:26,excludes:27,includes:28,todayMarker:29,title:30,acc_title:31,acc_title_value:32,acc_descr:33,acc_descr_value:34,acc_descr_multiline_value:35,section:36,clickStatement:37,taskTxt:38,taskData:39,click:40,callbackname:41,callbackargs:42,href:43,clickStatementDebug:44,$accept:0,$end:1},terminals_:{2:"error",4:"gantt",6:"EOF",8:"SPACE",10:"NL",12:"weekday_monday",13:"weekday_tuesday",14:"weekday_wednesday",15:"weekday_thursday",16:"weekday_friday",17:"weekday_saturday",18:"weekday_sunday",20:"weekend_friday",21:"weekend_saturday",22:"dateFormat",23:"inclusiveEndDates",24:"topAxis",25:"axisFormat",26:"tickInterval",27:"excludes",28:"includes",29:"todayMarker",30:"title",31:"acc_title",32:"acc_title_value",33:"acc_descr",34:"acc_descr_value",35:"acc_descr_multiline_value",36:"section",38:"taskTxt",39:"taskData",40:"click",41:"callbackname",42:"callbackargs",43:"href"},productions_:[0,[3,3],[5,0],[5,2],[7,2],[7,1],[7,1],[7,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[19,1],[19,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,2],[9,2],[9,1],[9,1],[9,1],[9,2],[37,2],[37,3],[37,3],[37,4],[37,3],[37,4],[37,2],[44,2],[44,3],[44,3],[44,4],[44,3],[44,4],[44,2]],performAction:(0,s.eW)(function(o,d,f,u,g,t,c){var r=t.length-1;switch(g){case 1:return t[r-1];case 2:this.$=[];break;case 3:t[r-1].push(t[r]),this.$=t[r-1];break;case 4:case 5:this.$=t[r];break;case 6:case 7:this.$=[];break;case 8:u.setWeekday("monday");break;case 9:u.setWeekday("tuesday");break;case 10:u.setWeekday("wednesday");break;case 11:u.setWeekday("thursday");break;case 12:u.setWeekday("friday");break;case 13:u.setWeekday("saturday");break;case 14:u.setWeekday("sunday");break;case 15:u.setWeekend("friday");break;case 16:u.setWeekend("saturday");break;case 17:u.setDateFormat(t[r].substr(11)),this.$=t[r].substr(11);break;case 18:u.enableInclusiveEndDates(),this.$=t[r].substr(18);break;case 19:u.TopAxis(),this.$=t[r].substr(8);break;case 20:u.setAxisFormat(t[r].substr(11)),this.$=t[r].substr(11);break;case 21:u.setTickInterval(t[r].substr(13)),this.$=t[r].substr(13);break;case 22:u.setExcludes(t[r].substr(9)),this.$=t[r].substr(9);break;case 23:u.setIncludes(t[r].substr(9)),this.$=t[r].substr(9);break;case 24:u.setTodayMarker(t[r].substr(12)),this.$=t[r].substr(12);break;case 27:u.setDiagramTitle(t[r].substr(6)),this.$=t[r].substr(6);break;case 28:this.$=t[r].trim(),u.setAccTitle(this.$);break;case 29:case 30:this.$=t[r].trim(),u.setAccDescription(this.$);break;case 31:u.addSection(t[r].substr(8)),this.$=t[r].substr(8);break;case 33:u.addTask(t[r-1],t[r]),this.$="task";break;case 34:this.$=t[r-1],u.setClickEvent(t[r-1],t[r],null);break;case 35:this.$=t[r-2],u.setClickEvent(t[r-2],t[r-1],t[r]);break;case 36:this.$=t[r-2],u.setClickEvent(t[r-2],t[r-1],null),u.setLink(t[r-2],t[r]);break;case 37:this.$=t[r-3],u.setClickEvent(t[r-3],t[r-2],t[r-1]),u.setLink(t[r-3],t[r]);break;case 38:this.$=t[r-2],u.setClickEvent(t[r-2],t[r],null),u.setLink(t[r-2],t[r-1]);break;case 39:this.$=t[r-3],u.setClickEvent(t[r-3],t[r-1],t[r]),u.setLink(t[r-3],t[r-2]);break;case 40:this.$=t[r-1],u.setLink(t[r-1],t[r]);break;case 41:case 47:this.$=t[r-1]+" "+t[r];break;case 42:case 43:case 45:this.$=t[r-2]+" "+t[r-1]+" "+t[r];break;case 44:case 46:this.$=t[r-3]+" "+t[r-2]+" "+t[r-1]+" "+t[r];break}},"anonymous"),table:[{3:1,4:[1,2]},{1:[3]},e(i,[2,2],{5:3}),{6:[1,4],7:5,8:[1,6],9:7,10:[1,8],11:17,12:a,13:l,14:n,15:h,16:k,17:O,18:B,19:18,20:N,21:C,22:L,23:K,24:V,25:R,26:w,27:re,28:se,29:ie,30:ae,31:ne,33:ce,35:le,36:oe,37:24,38:y,40:b},e(i,[2,7],{1:[2,1]}),e(i,[2,3]),{9:36,11:17,12:a,13:l,14:n,15:h,16:k,17:O,18:B,19:18,20:N,21:C,22:L,23:K,24:V,25:R,26:w,27:re,28:se,29:ie,30:ae,31:ne,33:ce,35:le,36:oe,37:24,38:y,40:b},e(i,[2,5]),e(i,[2,6]),e(i,[2,17]),e(i,[2,18]),e(i,[2,19]),e(i,[2,20]),e(i,[2,21]),e(i,[2,22]),e(i,[2,23]),e(i,[2,24]),e(i,[2,25]),e(i,[2,26]),e(i,[2,27]),{32:[1,37]},{34:[1,38]},e(i,[2,30]),e(i,[2,31]),e(i,[2,32]),{39:[1,39]},e(i,[2,8]),e(i,[2,9]),e(i,[2,10]),e(i,[2,11]),e(i,[2,12]),e(i,[2,13]),e(i,[2,14]),e(i,[2,15]),e(i,[2,16]),{41:[1,40],43:[1,41]},e(i,[2,4]),e(i,[2,28]),e(i,[2,29]),e(i,[2,33]),e(i,[2,34],{42:[1,42],43:[1,43]}),e(i,[2,40],{41:[1,44]}),e(i,[2,35],{43:[1,45]}),e(i,[2,36]),e(i,[2,38],{42:[1,46]}),e(i,[2,37]),e(i,[2,39])],defaultActions:{},parseError:(0,s.eW)(function(o,d){if(d.recoverable)this.trace(o);else{var f=new Error(o);throw f.hash=d,f}},"parseError"),parse:(0,s.eW)(function(o){var d=this,f=[0],u=[],g=[null],t=[],c=this.table,r="",E=0,_=0,W=0,F=2,D=1,Ie=t.slice.call(arguments,1),S=Object.create(this.lexer),Z={yy:{}};for(var Ae in this.yy)Object.prototype.hasOwnProperty.call(this.yy,Ae)&&(Z.yy[Ae]=this.yy[Ae]);S.setInput(o,Z.yy),Z.yy.lexer=S,Z.yy.parser=this,typeof S.yylloc=="undefined"&&(S.yylloc={});var Le=S.yylloc;t.push(Le);var Kt=S.options&&S.options.ranges;typeof Z.yy.parseError=="function"?this.parseError=Z.yy.parseError:this.parseError=Object.getPrototypeOf(this).parseError;function Xt(P){f.length=f.length-2*P,g.length=g.length-P,t.length=t.length-P}(0,s.eW)(Xt,"popStack");function Ge(){var P;return P=u.pop()||S.lex()||D,typeof P!="number"&&(P instanceof Array&&(u=P,P=u.pop()),P=d.symbols_[P]||P),P}(0,s.eW)(Ge,"lex");for(var M,Fe,q,Y,Zt,Me,Q={},he,X,Ze,ye;;){if(q=f[f.length-1],this.defaultActions[q]?Y=this.defaultActions[q]:((M===null||typeof M=="undefined")&&(M=Ge()),Y=c[q]&&c[q][M]),typeof Y=="undefined"||!Y.length||!Y[0]){var Oe="";ye=[];for(he in c[q])this.terminals_[he]&&he>F&&ye.push("'"+this.terminals_[he]+"'");S.showPosition?Oe="Parse error on line "+(E+1)+`:
`+S.showPosition()+`
Expecting `+ye.join(", ")+", got '"+(this.terminals_[M]||M)+"'":Oe="Parse error on line "+(E+1)+": Unexpected "+(M==D?"end of input":"'"+(this.terminals_[M]||M)+"'"),this.parseError(Oe,{text:S.match,token:this.terminals_[M]||M,line:S.yylineno,loc:Le,expected:ye})}if(Y[0]instanceof Array&&Y.length>1)throw new Error("Parse Error: multiple actions possible at state: "+q+", token: "+M);switch(Y[0]){case 1:f.push(M),g.push(S.yytext),t.push(S.yylloc),f.push(Y[1]),M=null,Fe?(M=Fe,Fe=null):(_=S.yyleng,r=S.yytext,E=S.yylineno,Le=S.yylloc,W>0&&W--);break;case 2:if(X=this.productions_[Y[1]][1],Q.$=g[g.length-X],Q._$={first_line:t[t.length-(X||1)].first_line,last_line:t[t.length-1].last_line,first_column:t[t.length-(X||1)].first_column,last_column:t[t.length-1].last_column},Kt&&(Q._$.range=[t[t.length-(X||1)].range[0],t[t.length-1].range[1]]),Me=this.performAction.apply(Q,[r,_,E,Z.yy,Y[1],g,t].concat(Ie)),typeof Me!="undefined")return Me;X&&(f=f.slice(0,-1*X*2),g=g.slice(0,-1*X),t=t.slice(0,-1*X)),f.push(this.productions_[Y[1]][0]),g.push(Q.$),t.push(Q._$),Ze=c[f[f.length-2]][f[f.length-1]],f.push(Ze);break;case 3:return!0}}return!0},"parse")},p=function(){var x={EOF:1,parseError:(0,s.eW)(function(d,f){if(this.yy.parser)this.yy.parser.parseError(d,f);else throw new Error(d)},"parseError"),setInput:(0,s.eW)(function(o,d){return this.yy=d||this.yy||{},this._input=o,this._more=this._backtrack=this.done=!1,this.yylineno=this.yyleng=0,this.yytext=this.matched=this.match="",this.conditionStack=["INITIAL"],this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0},this.options.ranges&&(this.yylloc.range=[0,0]),this.offset=0,this},"setInput"),input:(0,s.eW)(function(){var o=this._input[0];this.yytext+=o,this.yyleng++,this.offset++,this.match+=o,this.matched+=o;var d=o.match(/(?:\r\n?|\n).*/g);return d?(this.yylineno++,this.yylloc.last_line++):this.yylloc.last_column++,this.options.ranges&&this.yylloc.range[1]++,this._input=this._input.slice(1),o},"input"),unput:(0,s.eW)(function(o){var d=o.length,f=o.split(/(?:\r\n?|\n)/g);this._input=o+this._input,this.yytext=this.yytext.substr(0,this.yytext.length-d),this.offset-=d;var u=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1),this.matched=this.matched.substr(0,this.matched.length-1),f.length-1&&(this.yylineno-=f.length-1);var g=this.yylloc.range;return this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:f?(f.length===u.length?this.yylloc.first_column:0)+u[u.length-f.length].length-f[0].length:this.yylloc.first_column-d},this.options.ranges&&(this.yylloc.range=[g[0],g[0]+this.yyleng-d]),this.yyleng=this.yytext.length,this},"unput"),more:(0,s.eW)(function(){return this._more=!0,this},"more"),reject:(0,s.eW)(function(){if(this.options.backtrack_lexer)this._backtrack=!0;else return this.parseError("Lexical error on line "+(this.yylineno+1)+`. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
`+this.showPosition(),{text:"",token:null,line:this.yylineno});return this},"reject"),less:(0,s.eW)(function(o){this.unput(this.match.slice(o))},"less"),pastInput:(0,s.eW)(function(){var o=this.matched.substr(0,this.matched.length-this.match.length);return(o.length>20?"...":"")+o.substr(-20).replace(/\n/g,"")},"pastInput"),upcomingInput:(0,s.eW)(function(){var o=this.match;return o.length<20&&(o+=this._input.substr(0,20-o.length)),(o.substr(0,20)+(o.length>20?"...":"")).replace(/\n/g,"")},"upcomingInput"),showPosition:(0,s.eW)(function(){var o=this.pastInput(),d=new Array(o.length+1).join("-");return o+this.upcomingInput()+`
`+d+"^"},"showPosition"),test_match:(0,s.eW)(function(o,d){var f,u,g;if(this.options.backtrack_lexer&&(g={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done},this.options.ranges&&(g.yylloc.range=this.yylloc.range.slice(0))),u=o[0].match(/(?:\r\n?|\n).*/g),u&&(this.yylineno+=u.length),this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:u?u[u.length-1].length-u[u.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+o[0].length},this.yytext+=o[0],this.match+=o[0],this.matches=o,this.yyleng=this.yytext.length,this.options.ranges&&(this.yylloc.range=[this.offset,this.offset+=this.yyleng]),this._more=!1,this._backtrack=!1,this._input=this._input.slice(o[0].length),this.matched+=o[0],f=this.performAction.call(this,this.yy,this,d,this.conditionStack[this.conditionStack.length-1]),this.done&&this._input&&(this.done=!1),f)return f;if(this._backtrack){for(var t in g)this[t]=g[t];return!1}return!1},"test_match"),next:(0,s.eW)(function(){if(this.done)return this.EOF;this._input||(this.done=!0);var o,d,f,u;this._more||(this.yytext="",this.match="");for(var g=this._currentRules(),t=0;t<g.length;t++)if(f=this._input.match(this.rules[g[t]]),f&&(!d||f[0].length>d[0].length)){if(d=f,u=t,this.options.backtrack_lexer){if(o=this.test_match(f,g[t]),o!==!1)return o;if(this._backtrack){d=!1;continue}else return!1}else if(!this.options.flex)break}return d?(o=this.test_match(d,g[u]),o!==!1?o:!1):this._input===""?this.EOF:this.parseError("Lexical error on line "+(this.yylineno+1)+`. Unrecognized text.
`+this.showPosition(),{text:"",token:null,line:this.yylineno})},"next"),lex:(0,s.eW)(function(){var d=this.next();return d||this.lex()},"lex"),begin:(0,s.eW)(function(d){this.conditionStack.push(d)},"begin"),popState:(0,s.eW)(function(){var d=this.conditionStack.length-1;return d>0?this.conditionStack.pop():this.conditionStack[0]},"popState"),_currentRules:(0,s.eW)(function(){return this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]?this.conditions[this.conditionStack[this.conditionStack.length-1]].rules:this.conditions.INITIAL.rules},"_currentRules"),topState:(0,s.eW)(function(d){return d=this.conditionStack.length-1-Math.abs(d||0),d>=0?this.conditionStack[d]:"INITIAL"},"topState"),pushState:(0,s.eW)(function(d){this.begin(d)},"pushState"),stateStackSize:(0,s.eW)(function(){return this.conditionStack.length},"stateStackSize"),options:{"case-insensitive":!0},performAction:(0,s.eW)(function(d,f,u,g){var t=g;switch(u){case 0:return this.begin("open_directive"),"open_directive";break;case 1:return this.begin("acc_title"),31;break;case 2:return this.popState(),"acc_title_value";break;case 3:return this.begin("acc_descr"),33;break;case 4:return this.popState(),"acc_descr_value";break;case 5:this.begin("acc_descr_multiline");break;case 6:this.popState();break;case 7:return"acc_descr_multiline_value";case 8:break;case 9:break;case 10:break;case 11:return 10;case 12:break;case 13:break;case 14:this.begin("href");break;case 15:this.popState();break;case 16:return 43;case 17:this.begin("callbackname");break;case 18:this.popState();break;case 19:this.popState(),this.begin("callbackargs");break;case 20:return 41;case 21:this.popState();break;case 22:return 42;case 23:this.begin("click");break;case 24:this.popState();break;case 25:return 40;case 26:return 4;case 27:return 22;case 28:return 23;case 29:return 24;case 30:return 25;case 31:return 26;case 32:return 28;case 33:return 27;case 34:return 29;case 35:return 12;case 36:return 13;case 37:return 14;case 38:return 15;case 39:return 16;case 40:return 17;case 41:return 18;case 42:return 20;case 43:return 21;case 44:return"date";case 45:return 30;case 46:return"accDescription";case 47:return 36;case 48:return 38;case 49:return 39;case 50:return":";case 51:return 6;case 52:return"INVALID"}},"anonymous"),rules:[/^(?:%%\{)/i,/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:%%(?!\{)*[^\n]*)/i,/^(?:[^\}]%%*[^\n]*)/i,/^(?:%%*[^\n]*[\n]*)/i,/^(?:[\n]+)/i,/^(?:\s+)/i,/^(?:%[^\n]*)/i,/^(?:href[\s]+["])/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:call[\s]+)/i,/^(?:\([\s]*\))/i,/^(?:\()/i,/^(?:[^(]*)/i,/^(?:\))/i,/^(?:[^)]*)/i,/^(?:click[\s]+)/i,/^(?:[\s\n])/i,/^(?:[^\s\n]*)/i,/^(?:gantt\b)/i,/^(?:dateFormat\s[^#\n;]+)/i,/^(?:inclusiveEndDates\b)/i,/^(?:topAxis\b)/i,/^(?:axisFormat\s[^#\n;]+)/i,/^(?:tickInterval\s[^#\n;]+)/i,/^(?:includes\s[^#\n;]+)/i,/^(?:excludes\s[^#\n;]+)/i,/^(?:todayMarker\s[^\n;]+)/i,/^(?:weekday\s+monday\b)/i,/^(?:weekday\s+tuesday\b)/i,/^(?:weekday\s+wednesday\b)/i,/^(?:weekday\s+thursday\b)/i,/^(?:weekday\s+friday\b)/i,/^(?:weekday\s+saturday\b)/i,/^(?:weekday\s+sunday\b)/i,/^(?:weekend\s+friday\b)/i,/^(?:weekend\s+saturday\b)/i,/^(?:\d\d\d\d-\d\d-\d\d\b)/i,/^(?:title\s[^\n]+)/i,/^(?:accDescription\s[^#\n;]+)/i,/^(?:section\s[^\n]+)/i,/^(?:[^:\n]+)/i,/^(?::[^#\n;]+)/i,/^(?::)/i,/^(?:$)/i,/^(?:.)/i],conditions:{acc_descr_multiline:{rules:[6,7],inclusive:!1},acc_descr:{rules:[4],inclusive:!1},acc_title:{rules:[2],inclusive:!1},callbackargs:{rules:[21,22],inclusive:!1},callbackname:{rules:[18,19,20],inclusive:!1},href:{rules:[15,16],inclusive:!1},click:{rules:[24,25],inclusive:!1},INITIAL:{rules:[0,1,3,5,8,9,10,11,12,13,14,17,23,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52],inclusive:!0}}};return x}();v.lexer=p;function m(){this.yy={}}return(0,s.eW)(m,"Parser"),m.prototype=v,v.Parser=m,new m}();me.parser=me;var tt=me;A.extend(Qe),A.extend($e),A.extend(et);var Pe={friday:5,saturday:6},U="",ge="",ve=void 0,pe="",$=[],ee=[],be=new Map,Te=[],ue=[],H="",xe="",Ve=["active","done","crit","milestone","vert"],_e=[],te=!1,we=!1,We="sunday",de="saturday",Ee=0,rt=(0,s.eW)(function(){Te=[],ue=[],H="",_e=[],fe=0,Ce=void 0,ke=void 0,I=[],U="",ge="",xe="",ve=void 0,pe="",$=[],ee=[],te=!1,we=!1,Ee=0,be=new Map,(0,s.ZH)(),We="sunday",de="saturday"},"clear"),st=(0,s.eW)(function(e){ge=e},"setAxisFormat"),it=(0,s.eW)(function(){return ge},"getAxisFormat"),at=(0,s.eW)(function(e){ve=e},"setTickInterval"),nt=(0,s.eW)(function(){return ve},"getTickInterval"),ct=(0,s.eW)(function(e){pe=e},"setTodayMarker"),lt=(0,s.eW)(function(){return pe},"getTodayMarker"),ot=(0,s.eW)(function(e){U=e},"setDateFormat"),ut=(0,s.eW)(function(){te=!0},"enableInclusiveEndDates"),dt=(0,s.eW)(function(){return te},"endDatesAreInclusive"),ft=(0,s.eW)(function(){we=!0},"enableTopAxis"),kt=(0,s.eW)(function(){return we},"topAxisEnabled"),ht=(0,s.eW)(function(e){xe=e},"setDisplayMode"),yt=(0,s.eW)(function(){return xe},"getDisplayMode"),mt=(0,s.eW)(function(){return U},"getDateFormat"),gt=(0,s.eW)(function(e){$=e.toLowerCase().split(/[\s,]+/)},"setIncludes"),vt=(0,s.eW)(function(){return $},"getIncludes"),pt=(0,s.eW)(function(e){ee=e.toLowerCase().split(/[\s,]+/)},"setExcludes"),bt=(0,s.eW)(function(){return ee},"getExcludes"),Tt=(0,s.eW)(function(){return be},"getLinks"),xt=(0,s.eW)(function(e){H=e,Te.push(e)},"addSection"),_t=(0,s.eW)(function(){return Te},"getSections"),wt=(0,s.eW)(function(){let e=ze();const i=10;let a=0;for(;!e&&a<i;)e=ze(),a++;return ue=I,ue},"getTasks"),Re=(0,s.eW)(function(e,i,a,l){const n=e.format(i.trim()),h=e.format("YYYY-MM-DD");return l.includes(n)||l.includes(h)?!1:a.includes("weekends")&&(e.isoWeekday()===Pe[de]||e.isoWeekday()===Pe[de]+1)||a.includes(e.format("dddd").toLowerCase())?!0:a.includes(n)||a.includes(h)},"isInvalidDate"),Wt=(0,s.eW)(function(e){We=e},"setWeekday"),Et=(0,s.eW)(function(){return We},"getWeekday"),Dt=(0,s.eW)(function(e){de=e},"setWeekend"),Ye=(0,s.eW)(function(e,i,a,l){if(!a.length||e.manualEndTime)return;let n;e.startTime instanceof Date?n=A(e.startTime):n=A(e.startTime,i,!0),n=n.add(1,"d");let h;e.endTime instanceof Date?h=A(e.endTime):h=A(e.endTime,i,!0);const[k,O]=Ct(n,h,i,a,l);e.endTime=k.toDate(),e.renderEndTime=O},"checkTaskDates"),Ct=(0,s.eW)(function(e,i,a,l,n){let h=!1,k=null;for(;e<=i;)h||(k=i.toDate()),h=Re(e,a,l,n),h&&(i=i.add(1,"d")),e=e.add(1,"d");return[i,k]},"fixTaskDates"),De=(0,s.eW)(function(e,i,a){a=a.trim();const n=new RegExp("^after\\s+(?<ids>[\\d\\w- ]+)").exec(a);if(n!==null){let k=null;for(const B of n.groups.ids.split(" ")){let N=G(B);N!==void 0&&(!k||N.endTime>k.endTime)&&(k=N)}if(k)return k.endTime;const O=new Date;return O.setHours(0,0,0,0),O}let h=A(a,i.trim(),!0);if(h.isValid())return h.toDate();{s.cM.debug("Invalid date:"+a),s.cM.debug("With date format:"+i.trim());const k=new Date(a);if(k===void 0||isNaN(k.getTime())||k.getFullYear()<-1e4||k.getFullYear()>1e4)throw new Error("Invalid date:"+a);return k}},"getStartDate"),Be=(0,s.eW)(function(e){const i=/^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(e.trim());return i!==null?[Number.parseFloat(i[1]),i[2]]:[NaN,"ms"]},"parseDuration"),Ne=(0,s.eW)(function(e,i,a,l=!1){a=a.trim();const h=new RegExp("^until\\s+(?<ids>[\\d\\w- ]+)").exec(a);if(h!==null){let C=null;for(const K of h.groups.ids.split(" ")){let V=G(K);V!==void 0&&(!C||V.startTime<C.startTime)&&(C=V)}if(C)return C.startTime;const L=new Date;return L.setHours(0,0,0,0),L}let k=A(a,i.trim(),!0);if(k.isValid())return l&&(k=k.add(1,"d")),k.toDate();let O=A(e);const[B,N]=Be(a);if(!Number.isNaN(B)){const C=O.add(B,N);C.isValid()&&(O=C)}return O.toDate()},"getEndDate"),fe=0,J=(0,s.eW)(function(e){return e===void 0?(fe=fe+1,"task"+fe):e},"parseId"),St=(0,s.eW)(function(e,i){let a;i.substr(0,1)===":"?a=i.substr(1,i.length):a=i;const l=a.split(","),n={};Se(l,n,Ve);for(let k=0;k<l.length;k++)l[k]=l[k].trim();let h="";switch(l.length){case 1:n.id=J(),n.startTime=e.endTime,h=l[0];break;case 2:n.id=J(),n.startTime=De(void 0,U,l[0]),h=l[1];break;case 3:n.id=J(l[0]),n.startTime=De(void 0,U,l[1]),h=l[2];break;default:}return h&&(n.endTime=Ne(n.startTime,U,h,te),n.manualEndTime=A(h,"YYYY-MM-DD",!0).isValid(),Ye(n,U,ee,$)),n},"compileData"),It=(0,s.eW)(function(e,i){let a;i.substr(0,1)===":"?a=i.substr(1,i.length):a=i;const l=a.split(","),n={};Se(l,n,Ve);for(let h=0;h<l.length;h++)l[h]=l[h].trim();switch(l.length){case 1:n.id=J(),n.startTime={type:"prevTaskEnd",id:e},n.endTime={data:l[0]};break;case 2:n.id=J(),n.startTime={type:"getStartDate",startData:l[0]},n.endTime={data:l[1]};break;case 3:n.id=J(l[0]),n.startTime={type:"getStartDate",startData:l[1]},n.endTime={data:l[2]};break;default:}return n},"parseData"),Ce,ke,I=[],Ue={},At=(0,s.eW)(function(e,i){const a={section:H,type:H,processed:!1,manualEndTime:!1,renderEndTime:null,raw:{data:i},task:e,classes:[]},l=It(ke,i);a.raw.startTime=l.startTime,a.raw.endTime=l.endTime,a.id=l.id,a.prevTaskId=ke,a.active=l.active,a.done=l.done,a.crit=l.crit,a.milestone=l.milestone,a.vert=l.vert,a.order=Ee,Ee++;const n=I.push(a);ke=a.id,Ue[a.id]=n-1},"addTask"),G=(0,s.eW)(function(e){const i=Ue[e];return I[i]},"findTaskById"),Lt=(0,s.eW)(function(e,i){const a={section:H,type:H,description:e,task:e,classes:[]},l=St(Ce,i);a.startTime=l.startTime,a.endTime=l.endTime,a.id=l.id,a.active=l.active,a.done=l.done,a.crit=l.crit,a.milestone=l.milestone,a.vert=l.vert,Ce=a,ue.push(a)},"addTaskOrg"),ze=(0,s.eW)(function(){const e=(0,s.eW)(function(a){const l=I[a];let n="";switch(I[a].raw.startTime.type){case"prevTaskEnd":{const h=G(l.prevTaskId);l.startTime=h.endTime;break}case"getStartDate":n=De(void 0,U,I[a].raw.startTime.startData),n&&(I[a].startTime=n);break}return I[a].startTime&&(I[a].endTime=Ne(I[a].startTime,U,I[a].raw.endTime.data,te),I[a].endTime&&(I[a].processed=!0,I[a].manualEndTime=A(I[a].raw.endTime.data,"YYYY-MM-DD",!0).isValid(),Ye(I[a],U,ee,$))),I[a].processed},"compileTask");let i=!0;for(const[a,l]of I.entries())e(a),i=i&&l.processed;return i},"compileTasks"),Ft=(0,s.eW)(function(e,i){let a=i;(0,s.nV)().securityLevel!=="loose"&&(a=(0,Je.N)(i)),e.split(",").forEach(function(l){G(l)!==void 0&&(Ke(l,()=>{window.open(a,"_self")}),be.set(l,a))}),je(e,"clickable")},"setLink"),je=(0,s.eW)(function(e,i){e.split(",").forEach(function(a){let l=G(a);l!==void 0&&l.classes.push(i)})},"setClass"),Mt=(0,s.eW)(function(e,i,a){if((0,s.nV)().securityLevel!=="loose"||i===void 0)return;let l=[];if(typeof a=="string"){l=a.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);for(let h=0;h<l.length;h++){let k=l[h].trim();k.startsWith('"')&&k.endsWith('"')&&(k=k.substr(1,k.length-2)),l[h]=k}}l.length===0&&l.push(e),G(e)!==void 0&&Ke(e,()=>{He.w8.runFunc(i,...l)})},"setClickFun"),Ke=(0,s.eW)(function(e,i){_e.push(function(){const a=document.querySelector(`[id="${e}"]`);a!==null&&a.addEventListener("click",function(){i()})},function(){const a=document.querySelector(`[id="${e}-text"]`);a!==null&&a.addEventListener("click",function(){i()})})},"pushFun"),Ot=(0,s.eW)(function(e,i,a){e.split(",").forEach(function(l){Mt(l,i,a)}),je(e,"clickable")},"setClickEvent"),Pt=(0,s.eW)(function(e){_e.forEach(function(i){i(e)})},"bindFunctions"),Vt={getConfig:(0,s.eW)(()=>(0,s.nV)().gantt,"getConfig"),clear:rt,setDateFormat:ot,getDateFormat:mt,enableInclusiveEndDates:ut,endDatesAreInclusive:dt,enableTopAxis:ft,topAxisEnabled:kt,setAxisFormat:st,getAxisFormat:it,setTickInterval:at,getTickInterval:nt,setTodayMarker:ct,getTodayMarker:lt,setAccTitle:s.GN,getAccTitle:s.eu,setDiagramTitle:s.g2,getDiagramTitle:s.Kr,setDisplayMode:ht,getDisplayMode:yt,setAccDescription:s.U$,getAccDescription:s.Mx,addSection:xt,getSections:_t,getTasks:wt,addTask:At,findTaskById:G,addTaskOrg:Lt,setIncludes:gt,getIncludes:vt,setExcludes:pt,getExcludes:bt,setClickEvent:Ot,setLink:Ft,getLinks:Tt,bindFunctions:Pt,parseDuration:Be,isInvalidDate:Re,setWeekday:Wt,getWeekday:Et,setWeekend:Dt};function Se(e,i,a){let l=!0;for(;l;)l=!1,a.forEach(function(n){const h="^\\s*"+n+"\\s*$",k=new RegExp(h);e[0].match(k)&&(i[n]=!0,e.shift(1),l=!0)})}(0,s.eW)(Se,"getTaskTags");var Rt=(0,s.eW)(function(){s.cM.debug("Something is calling, setConf, remove the call")},"setConf"),Xe={monday:T.Ox9,tuesday:T.YDX,wednesday:T.EFj,thursday:T.Igq,friday:T.y2j,saturday:T.LqH,sunday:T.Zyz},Yt=(0,s.eW)((e,i)=>{let a=[...e].map(()=>-1/0),l=[...e].sort((h,k)=>h.startTime-k.startTime||h.order-k.order),n=0;for(const h of l)for(let k=0;k<a.length;k++)if(h.startTime>=a[k]){a[k]=h.endTime,h.order=k+i,k>n&&(n=k);break}return n},"getMaxIntersections"),j,Bt=(0,s.eW)(function(e,i,a,l){const n=(0,s.nV)().gantt,h=(0,s.nV)().securityLevel;let k;h==="sandbox"&&(k=(0,T.Ys)("#i"+i));const O=h==="sandbox"?(0,T.Ys)(k.nodes()[0].contentDocument.body):(0,T.Ys)("body"),B=h==="sandbox"?k.nodes()[0].contentDocument:document,N=B.getElementById(i);j=N.parentElement.offsetWidth,j===void 0&&(j=1200),n.useWidth!==void 0&&(j=n.useWidth);const C=l.db.getTasks();let L=[];for(const y of C)L.push(y.type);L=oe(L);const K={};let V=2*n.topPadding;if(l.db.getDisplayMode()==="compact"||n.displayMode==="compact"){const y={};for(const v of C)y[v.section]===void 0?y[v.section]=[v]:y[v.section].push(v);let b=0;for(const v of Object.keys(y)){const p=Yt(y[v],b)+1;b+=p,V+=p*(n.barHeight+n.barGap),K[v]=p}}else{V+=C.length*(n.barHeight+n.barGap);for(const y of L)K[y]=C.filter(b=>b.type===y).length}N.setAttribute("viewBox","0 0 "+j+" "+V);const R=O.select(`[id="${i}"]`),w=(0,T.Xf)().domain([(0,T.VV$)(C,function(y){return y.startTime}),(0,T.Fp7)(C,function(y){return y.endTime})]).rangeRound([0,j-n.leftPadding-n.rightPadding]);function re(y,b){const v=y.startTime,p=b.startTime;let m=0;return v>p?m=1:v<p&&(m=-1),m}(0,s.eW)(re,"taskCompare"),C.sort(re),se(C,j,V),(0,s.v2)(R,V,j,n.useMaxWidth),R.append("text").text(l.db.getDiagramTitle()).attr("x",j/2).attr("y",n.titleTopMargin).attr("class","titleText");function se(y,b,v){const p=n.barHeight,m=p+n.barGap,x=n.topPadding,o=n.leftPadding,d=(0,T.BYU)().domain([0,L.length]).range(["#00B9FA","#F95002"]).interpolate(T.JHv);ae(m,x,o,b,v,y,l.db.getExcludes(),l.db.getIncludes()),ne(o,x,b,v),ie(y,m,x,o,p,d,b,v),ce(m,x,o,p,d),le(o,x,b,v)}(0,s.eW)(se,"makeGantt");function ie(y,b,v,p,m,x,o){y.sort((c,r)=>c.vert===r.vert?0:c.vert?1:-1);const f=[...new Set(y.map(c=>c.order))].map(c=>y.find(r=>r.order===c));R.append("g").selectAll("rect").data(f).enter().append("rect").attr("x",0).attr("y",function(c,r){return r=c.order,r*b+v-2}).attr("width",function(){return o-n.rightPadding/2}).attr("height",b).attr("class",function(c){for(const[r,E]of L.entries())if(c.type===E)return"section section"+r%n.numberSectionStyles;return"section section0"}).enter();const u=R.append("g").selectAll("rect").data(y).enter(),g=l.db.getLinks();if(u.append("rect").attr("id",function(c){return c.id}).attr("rx",3).attr("ry",3).attr("x",function(c){return c.milestone?w(c.startTime)+p+.5*(w(c.endTime)-w(c.startTime))-.5*m:w(c.startTime)+p}).attr("y",function(c,r){return r=c.order,c.vert?n.gridLineStartPadding:r*b+v}).attr("width",function(c){return c.milestone?m:c.vert?.08*m:w(c.renderEndTime||c.endTime)-w(c.startTime)}).attr("height",function(c){return c.vert?C.length*(n.barHeight+n.barGap)+n.barHeight*2:m}).attr("transform-origin",function(c,r){return r=c.order,(w(c.startTime)+p+.5*(w(c.endTime)-w(c.startTime))).toString()+"px "+(r*b+v+.5*m).toString()+"px"}).attr("class",function(c){const r="task";let E="";c.classes.length>0&&(E=c.classes.join(" "));let _=0;for(const[F,D]of L.entries())c.type===D&&(_=F%n.numberSectionStyles);let W="";return c.active?c.crit?W+=" activeCrit":W=" active":c.done?c.crit?W=" doneCrit":W=" done":c.crit&&(W+=" crit"),W.length===0&&(W=" task"),c.milestone&&(W=" milestone "+W),c.vert&&(W=" vert "+W),W+=_,W+=" "+E,r+W}),u.append("text").attr("id",function(c){return c.id+"-text"}).text(function(c){return c.task}).attr("font-size",n.fontSize).attr("x",function(c){let r=w(c.startTime),E=w(c.renderEndTime||c.endTime);if(c.milestone&&(r+=.5*(w(c.endTime)-w(c.startTime))-.5*m,E=r+m),c.vert)return w(c.startTime)+p;const _=this.getBBox().width;return _>E-r?E+_+1.5*n.leftPadding>o?r+p-5:E+p+5:(E-r)/2+r+p}).attr("y",function(c,r){return c.vert?n.gridLineStartPadding+C.length*(n.barHeight+n.barGap)+60:(r=c.order,r*b+n.barHeight/2+(n.fontSize/2-2)+v)}).attr("text-height",m).attr("class",function(c){const r=w(c.startTime);let E=w(c.endTime);c.milestone&&(E=r+m);const _=this.getBBox().width;let W="";c.classes.length>0&&(W=c.classes.join(" "));let F=0;for(const[Ie,S]of L.entries())c.type===S&&(F=Ie%n.numberSectionStyles);let D="";return c.active&&(c.crit?D="activeCritText"+F:D="activeText"+F),c.done?c.crit?D=D+" doneCritText"+F:D=D+" doneText"+F:c.crit&&(D=D+" critText"+F),c.milestone&&(D+=" milestoneText"),c.vert&&(D+=" vertText"),_>E-r?E+_+1.5*n.leftPadding>o?W+" taskTextOutsideLeft taskTextOutside"+F+" "+D:W+" taskTextOutsideRight taskTextOutside"+F+" "+D+" width-"+_:W+" taskText taskText"+F+" "+D+" width-"+_}),(0,s.nV)().securityLevel==="sandbox"){let c;c=(0,T.Ys)("#i"+i);const r=c.nodes()[0].contentDocument;u.filter(function(E){return g.has(E.id)}).each(function(E){var _=r.querySelector("#"+E.id),W=r.querySelector("#"+E.id+"-text");const F=_.parentNode;var D=r.createElement("a");D.setAttribute("xlink:href",g.get(E.id)),D.setAttribute("target","_top"),F.appendChild(D),D.appendChild(_),D.appendChild(W)})}}(0,s.eW)(ie,"drawRects");function ae(y,b,v,p,m,x,o,d){if(o.length===0&&d.length===0)return;let f,u;for(const{startTime:_,endTime:W}of x)(f===void 0||_<f)&&(f=_),(u===void 0||W>u)&&(u=W);if(!f||!u)return;if(A(u).diff(A(f),"year")>5){s.cM.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");return}const g=l.db.getDateFormat(),t=[];let c=null,r=A(f);for(;r.valueOf()<=u;)l.db.isInvalidDate(r,g,o,d)?c?c.end=r:c={start:r,end:r}:c&&(t.push(c),c=null),r=r.add(1,"d");R.append("g").selectAll("rect").data(t).enter().append("rect").attr("id",_=>"exclude-"+_.start.format("YYYY-MM-DD")).attr("x",_=>w(_.start.startOf("day"))+v).attr("y",n.gridLineStartPadding).attr("width",_=>w(_.end.endOf("day"))-w(_.start.startOf("day"))).attr("height",m-b-n.gridLineStartPadding).attr("transform-origin",function(_,W){return(w(_.start)+v+.5*(w(_.end)-w(_.start))).toString()+"px "+(W*y+.5*m).toString()+"px"}).attr("class","exclude-range")}(0,s.eW)(ae,"drawExcludeDays");function ne(y,b,v,p){var g;const m=l.db.getDateFormat(),x=l.db.getAxisFormat();let o;x?o=x:m==="D"?o="%d":o=(g=n.axisFormat)!=null?g:"%Y-%m-%d";let d=(0,T.LLu)(w).tickSize(-p+b+n.gridLineStartPadding).tickFormat((0,T.i$Z)(o));const u=/^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(l.db.getTickInterval()||n.tickInterval);if(u!==null){const t=u[1],c=u[2],r=l.db.getWeekday()||n.weekday;switch(c){case"millisecond":d.ticks(T.U8T.every(t));break;case"second":d.ticks(T.S1K.every(t));break;case"minute":d.ticks(T.Z_i.every(t));break;case"hour":d.ticks(T.WQD.every(t));break;case"day":d.ticks(T.rr1.every(t));break;case"week":d.ticks(Xe[r].every(t));break;case"month":d.ticks(T.F0B.every(t));break}}if(R.append("g").attr("class","grid").attr("transform","translate("+y+", "+(p-50)+")").call(d).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10).attr("dy","1em"),l.db.topAxisEnabled()||n.topAxis){let t=(0,T.F5q)(w).tickSize(-p+b+n.gridLineStartPadding).tickFormat((0,T.i$Z)(o));if(u!==null){const c=u[1],r=u[2],E=l.db.getWeekday()||n.weekday;switch(r){case"millisecond":t.ticks(T.U8T.every(c));break;case"second":t.ticks(T.S1K.every(c));break;case"minute":t.ticks(T.Z_i.every(c));break;case"hour":t.ticks(T.WQD.every(c));break;case"day":t.ticks(T.rr1.every(c));break;case"week":t.ticks(Xe[E].every(c));break;case"month":t.ticks(T.F0B.every(c));break}}R.append("g").attr("class","grid").attr("transform","translate("+y+", "+b+")").call(t).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10)}}(0,s.eW)(ne,"makeGrid");function ce(y,b){let v=0;const p=Object.keys(K).map(m=>[m,K[m]]);R.append("g").selectAll("text").data(p).enter().append(function(m){const x=m[0].split(s.SY.lineBreakRegex),o=-(x.length-1)/2,d=B.createElementNS("http://www.w3.org/2000/svg","text");d.setAttribute("dy",o+"em");for(const[f,u]of x.entries()){const g=B.createElementNS("http://www.w3.org/2000/svg","tspan");g.setAttribute("alignment-baseline","central"),g.setAttribute("x","10"),f>0&&g.setAttribute("dy","1em"),g.textContent=u,d.appendChild(g)}return d}).attr("x",10).attr("y",function(m,x){if(x>0)for(let o=0;o<x;o++)return v+=p[x-1][1],m[1]*y/2+v*y+b;else return m[1]*y/2+b}).attr("font-size",n.sectionFontSize).attr("class",function(m){for(const[x,o]of L.entries())if(m[0]===o)return"sectionTitle sectionTitle"+x%n.numberSectionStyles;return"sectionTitle"})}(0,s.eW)(ce,"vertLabels");function le(y,b,v,p){const m=l.db.getTodayMarker();if(m==="off")return;const x=R.append("g").attr("class","today"),o=new Date,d=x.append("line");d.attr("x1",w(o)+y).attr("x2",w(o)+y).attr("y1",n.titleTopMargin).attr("y2",p-n.titleTopMargin).attr("class","today"),m!==""&&d.attr("style",m.replace(/,/g,";"))}(0,s.eW)(le,"drawToday");function oe(y){const b={},v=[];for(let p=0,m=y.length;p<m;++p)Object.prototype.hasOwnProperty.call(b,y[p])||(b[y[p]]=!0,v.push(y[p]));return v}(0,s.eW)(oe,"checkUnique")},"draw"),Nt={setConf:Rt,draw:Bt},Ut=(0,s.eW)(e=>`
  .mermaid-main-font {
        font-family: ${e.fontFamily};
  }

  .exclude-range {
    fill: ${e.excludeBkgColor};
  }

  .section {
    stroke: none;
    opacity: 0.2;
  }

  .section0 {
    fill: ${e.sectionBkgColor};
  }

  .section2 {
    fill: ${e.sectionBkgColor2};
  }

  .section1,
  .section3 {
    fill: ${e.altSectionBkgColor};
    opacity: 0.2;
  }

  .sectionTitle0 {
    fill: ${e.titleColor};
  }

  .sectionTitle1 {
    fill: ${e.titleColor};
  }

  .sectionTitle2 {
    fill: ${e.titleColor};
  }

  .sectionTitle3 {
    fill: ${e.titleColor};
  }

  .sectionTitle {
    text-anchor: start;
    font-family: ${e.fontFamily};
  }


  /* Grid and axis */

  .grid .tick {
    stroke: ${e.gridColor};
    opacity: 0.8;
    shape-rendering: crispEdges;
  }

  .grid .tick text {
    font-family: ${e.fontFamily};
    fill: ${e.textColor};
  }

  .grid path {
    stroke-width: 0;
  }


  /* Today line */

  .today {
    fill: none;
    stroke: ${e.todayLineColor};
    stroke-width: 2px;
  }


  /* Task styling */

  /* Default task */

  .task {
    stroke-width: 2;
  }

  .taskText {
    text-anchor: middle;
    font-family: ${e.fontFamily};
  }

  .taskTextOutsideRight {
    fill: ${e.taskTextDarkColor};
    text-anchor: start;
    font-family: ${e.fontFamily};
  }

  .taskTextOutsideLeft {
    fill: ${e.taskTextDarkColor};
    text-anchor: end;
  }


  /* Special case clickable */

  .task.clickable {
    cursor: pointer;
  }

  .taskText.clickable {
    cursor: pointer;
    fill: ${e.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideLeft.clickable {
    cursor: pointer;
    fill: ${e.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideRight.clickable {
    cursor: pointer;
    fill: ${e.taskTextClickableColor} !important;
    font-weight: bold;
  }


  /* Specific task settings for the sections*/

  .taskText0,
  .taskText1,
  .taskText2,
  .taskText3 {
    fill: ${e.taskTextColor};
  }

  .task0,
  .task1,
  .task2,
  .task3 {
    fill: ${e.taskBkgColor};
    stroke: ${e.taskBorderColor};
  }

  .taskTextOutside0,
  .taskTextOutside2
  {
    fill: ${e.taskTextOutsideColor};
  }

  .taskTextOutside1,
  .taskTextOutside3 {
    fill: ${e.taskTextOutsideColor};
  }


  /* Active task */

  .active0,
  .active1,
  .active2,
  .active3 {
    fill: ${e.activeTaskBkgColor};
    stroke: ${e.activeTaskBorderColor};
  }

  .activeText0,
  .activeText1,
  .activeText2,
  .activeText3 {
    fill: ${e.taskTextDarkColor} !important;
  }


  /* Completed task */

  .done0,
  .done1,
  .done2,
  .done3 {
    stroke: ${e.doneTaskBorderColor};
    fill: ${e.doneTaskBkgColor};
    stroke-width: 2;
  }

  .doneText0,
  .doneText1,
  .doneText2,
  .doneText3 {
    fill: ${e.taskTextDarkColor} !important;
  }


  /* Tasks on the critical line */

  .crit0,
  .crit1,
  .crit2,
  .crit3 {
    stroke: ${e.critBorderColor};
    fill: ${e.critBkgColor};
    stroke-width: 2;
  }

  .activeCrit0,
  .activeCrit1,
  .activeCrit2,
  .activeCrit3 {
    stroke: ${e.critBorderColor};
    fill: ${e.activeTaskBkgColor};
    stroke-width: 2;
  }

  .doneCrit0,
  .doneCrit1,
  .doneCrit2,
  .doneCrit3 {
    stroke: ${e.critBorderColor};
    fill: ${e.doneTaskBkgColor};
    stroke-width: 2;
    cursor: pointer;
    shape-rendering: crispEdges;
  }

  .milestone {
    transform: rotate(45deg) scale(0.8,0.8);
  }

  .milestoneText {
    font-style: italic;
  }
  .doneCritText0,
  .doneCritText1,
  .doneCritText2,
  .doneCritText3 {
    fill: ${e.taskTextDarkColor} !important;
  }

  .vert {
    stroke: ${e.vertLineColor};
  }

  .vertText {
    font-size: 15px;
    text-anchor: middle;
    fill: ${e.vertLineColor} !important;
  }

  .activeCritText0,
  .activeCritText1,
  .activeCritText2,
  .activeCritText3 {
    fill: ${e.taskTextDarkColor} !important;
  }

  .titleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${e.titleColor||e.textColor};
    font-family: ${e.fontFamily};
  }
`,"getStyles"),zt=Ut,jt={parser:tt,db:Vt,renderer:Nt,styles:zt}}}]);
