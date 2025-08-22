!(function(){"use strict";var re=(St,Q,m)=>new Promise(($,B)=>{var Z=b=>{try{s(m.next(b))}catch(v){B(v)}},F=b=>{try{s(m.throw(b))}catch(v){B(v)}},s=b=>b.done?$(b.value):Promise.resolve(b.value).then(Z,F);s((m=m.apply(St,Q)).next())});(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[4595],{67378:function(St,Q,m){m.d(Q,{q:function(){return Z}});var $=m(32426),B=m(3466),Z=(0,$.eW)((F,s)=>{let b;return s==="sandbox"&&(b=(0,B.Ys)("#i"+F)),(s==="sandbox"?(0,B.Ys)(b.nodes()[0].contentDocument.body):(0,B.Ys)("body")).select(`[id="${F}"]`)},"getDiagramElement")},64595:function(St,Q,m){var q;m.d(Q,{Ee:function(){return Re},J8:function(){return v},_$:function(){return Ce},oI:function(){return Le}});var $=m(67378),B=m(88589),Z=m(28344),F=m(8111),s=m(32426),b=function(){var e=(0,s.eW)(function(J,c,d,o){for(d=d||{},o=J.length;o--;d[J[o]]=c);return d},"o"),t=[1,2],i=[1,3],n=[1,4],r=[2,4],l=[1,9],u=[1,11],S=[1,16],p=[1,17],g=[1,18],E=[1,19],k=[1,33],M=[1,20],P=[1,21],A=[1,22],R=[1,23],I=[1,24],f=[1,26],O=[1,27],x=[1,28],G=[1,29],Y=[1,30],w=[1,31],U=[1,32],tt=[1,35],Et=[1,36],Tt=[1,37],bt=[1,38],at=[1,34],y=[1,4,5,16,17,19,21,22,24,25,26,27,28,29,33,35,37,38,41,45,48,51,52,53,54,57],kt=[1,4,5,14,15,16,17,19,21,22,24,25,26,27,28,29,33,35,37,38,39,40,41,45,48,51,52,53,54,57],ee=[4,5,16,17,19,21,22,24,25,26,27,28,29,33,35,37,38,41,45,48,51,52,53,54,57],Rt={trace:(0,s.eW)(function(){},"trace"),yy:{},symbols_:{error:2,start:3,SPACE:4,NL:5,SD:6,document:7,line:8,statement:9,classDefStatement:10,styleStatement:11,cssClassStatement:12,idStatement:13,DESCR:14,"-->":15,HIDE_EMPTY:16,scale:17,WIDTH:18,COMPOSIT_STATE:19,STRUCT_START:20,STRUCT_STOP:21,STATE_DESCR:22,AS:23,ID:24,FORK:25,JOIN:26,CHOICE:27,CONCURRENT:28,note:29,notePosition:30,NOTE_TEXT:31,direction:32,acc_title:33,acc_title_value:34,acc_descr:35,acc_descr_value:36,acc_descr_multiline_value:37,CLICK:38,STRING:39,HREF:40,classDef:41,CLASSDEF_ID:42,CLASSDEF_STYLEOPTS:43,DEFAULT:44,style:45,STYLE_IDS:46,STYLEDEF_STYLEOPTS:47,class:48,CLASSENTITY_IDS:49,STYLECLASS:50,direction_tb:51,direction_bt:52,direction_rl:53,direction_lr:54,eol:55,";":56,EDGE_STATE:57,STYLE_SEPARATOR:58,left_of:59,right_of:60,$accept:0,$end:1},terminals_:{2:"error",4:"SPACE",5:"NL",6:"SD",14:"DESCR",15:"-->",16:"HIDE_EMPTY",17:"scale",18:"WIDTH",19:"COMPOSIT_STATE",20:"STRUCT_START",21:"STRUCT_STOP",22:"STATE_DESCR",23:"AS",24:"ID",25:"FORK",26:"JOIN",27:"CHOICE",28:"CONCURRENT",29:"note",31:"NOTE_TEXT",33:"acc_title",34:"acc_title_value",35:"acc_descr",36:"acc_descr_value",37:"acc_descr_multiline_value",38:"CLICK",39:"STRING",40:"HREF",41:"classDef",42:"CLASSDEF_ID",43:"CLASSDEF_STYLEOPTS",44:"DEFAULT",45:"style",46:"STYLE_IDS",47:"STYLEDEF_STYLEOPTS",48:"class",49:"CLASSENTITY_IDS",50:"STYLECLASS",51:"direction_tb",52:"direction_bt",53:"direction_rl",54:"direction_lr",56:";",57:"EDGE_STATE",58:"STYLE_SEPARATOR",59:"left_of",60:"right_of"},productions_:[0,[3,2],[3,2],[3,2],[7,0],[7,2],[8,2],[8,1],[8,1],[9,1],[9,1],[9,1],[9,1],[9,2],[9,3],[9,4],[9,1],[9,2],[9,1],[9,4],[9,3],[9,6],[9,1],[9,1],[9,1],[9,1],[9,4],[9,4],[9,1],[9,2],[9,2],[9,1],[9,5],[9,5],[10,3],[10,3],[11,3],[12,3],[32,1],[32,1],[32,1],[32,1],[55,1],[55,1],[13,1],[13,1],[13,3],[13,3],[30,1],[30,1]],performAction:(0,s.eW)(function(c,d,o,_,T,a,ft){var h=a.length-1;switch(T){case 3:return _.setRootDoc(a[h]),a[h];break;case 4:this.$=[];break;case 5:a[h]!="nl"&&(a[h-1].push(a[h]),this.$=a[h-1]);break;case 6:case 7:this.$=a[h];break;case 8:this.$="nl";break;case 12:this.$=a[h];break;case 13:const Dt=a[h-1];Dt.description=_.trimColon(a[h]),this.$=Dt;break;case 14:this.$={stmt:"relation",state1:a[h-2],state2:a[h]};break;case 15:const vt=_.trimColon(a[h]);this.$={stmt:"relation",state1:a[h-3],state2:a[h-1],description:vt};break;case 19:this.$={stmt:"state",id:a[h-3],type:"default",description:"",doc:a[h-1]};break;case 20:var et=a[h],nt=a[h-2].trim();if(a[h].match(":")){var pt=a[h].split(":");et=pt[0],nt=[nt,pt[1]]}this.$={stmt:"state",id:et,type:"default",description:nt};break;case 21:this.$={stmt:"state",id:a[h-3],type:"default",description:a[h-5],doc:a[h-1]};break;case 22:this.$={stmt:"state",id:a[h],type:"fork"};break;case 23:this.$={stmt:"state",id:a[h],type:"join"};break;case 24:this.$={stmt:"state",id:a[h],type:"choice"};break;case 25:this.$={stmt:"state",id:_.getDividerId(),type:"divider"};break;case 26:this.$={stmt:"state",id:a[h-1].trim(),note:{position:a[h-2].trim(),text:a[h].trim()}};break;case 29:this.$=a[h].trim(),_.setAccTitle(this.$);break;case 30:case 31:this.$=a[h].trim(),_.setAccDescription(this.$);break;case 32:this.$={stmt:"click",id:a[h-3],url:a[h-2],tooltip:a[h-1]};break;case 33:this.$={stmt:"click",id:a[h-3],url:a[h-1],tooltip:""};break;case 34:case 35:this.$={stmt:"classDef",id:a[h-1].trim(),classes:a[h].trim()};break;case 36:this.$={stmt:"style",id:a[h-1].trim(),styleClass:a[h].trim()};break;case 37:this.$={stmt:"applyClass",id:a[h-1].trim(),styleClass:a[h].trim()};break;case 38:_.setDirection("TB"),this.$={stmt:"dir",value:"TB"};break;case 39:_.setDirection("BT"),this.$={stmt:"dir",value:"BT"};break;case 40:_.setDirection("RL"),this.$={stmt:"dir",value:"RL"};break;case 41:_.setDirection("LR"),this.$={stmt:"dir",value:"LR"};break;case 44:case 45:this.$={stmt:"state",id:a[h].trim(),type:"default",description:""};break;case 46:this.$={stmt:"state",id:a[h-2].trim(),classes:[a[h].trim()],type:"default",description:""};break;case 47:this.$={stmt:"state",id:a[h-2].trim(),classes:[a[h].trim()],type:"default",description:""};break}},"anonymous"),table:[{3:1,4:t,5:i,6:n},{1:[3]},{3:5,4:t,5:i,6:n},{3:6,4:t,5:i,6:n},e([1,4,5,16,17,19,22,24,25,26,27,28,29,33,35,37,38,41,45,48,51,52,53,54,57],r,{7:7}),{1:[2,1]},{1:[2,2]},{1:[2,3],4:l,5:u,8:8,9:10,10:12,11:13,12:14,13:15,16:S,17:p,19:g,22:E,24:k,25:M,26:P,27:A,28:R,29:I,32:25,33:f,35:O,37:x,38:G,41:Y,45:w,48:U,51:tt,52:Et,53:Tt,54:bt,57:at},e(y,[2,5]),{9:39,10:12,11:13,12:14,13:15,16:S,17:p,19:g,22:E,24:k,25:M,26:P,27:A,28:R,29:I,32:25,33:f,35:O,37:x,38:G,41:Y,45:w,48:U,51:tt,52:Et,53:Tt,54:bt,57:at},e(y,[2,7]),e(y,[2,8]),e(y,[2,9]),e(y,[2,10]),e(y,[2,11]),e(y,[2,12],{14:[1,40],15:[1,41]}),e(y,[2,16]),{18:[1,42]},e(y,[2,18],{20:[1,43]}),{23:[1,44]},e(y,[2,22]),e(y,[2,23]),e(y,[2,24]),e(y,[2,25]),{30:45,31:[1,46],59:[1,47],60:[1,48]},e(y,[2,28]),{34:[1,49]},{36:[1,50]},e(y,[2,31]),{13:51,24:k,57:at},{42:[1,52],44:[1,53]},{46:[1,54]},{49:[1,55]},e(kt,[2,44],{58:[1,56]}),e(kt,[2,45],{58:[1,57]}),e(y,[2,38]),e(y,[2,39]),e(y,[2,40]),e(y,[2,41]),e(y,[2,6]),e(y,[2,13]),{13:58,24:k,57:at},e(y,[2,17]),e(ee,r,{7:59}),{24:[1,60]},{24:[1,61]},{23:[1,62]},{24:[2,48]},{24:[2,49]},e(y,[2,29]),e(y,[2,30]),{39:[1,63],40:[1,64]},{43:[1,65]},{43:[1,66]},{47:[1,67]},{50:[1,68]},{24:[1,69]},{24:[1,70]},e(y,[2,14],{14:[1,71]}),{4:l,5:u,8:8,9:10,10:12,11:13,12:14,13:15,16:S,17:p,19:g,21:[1,72],22:E,24:k,25:M,26:P,27:A,28:R,29:I,32:25,33:f,35:O,37:x,38:G,41:Y,45:w,48:U,51:tt,52:Et,53:Tt,54:bt,57:at},e(y,[2,20],{20:[1,73]}),{31:[1,74]},{24:[1,75]},{39:[1,76]},{39:[1,77]},e(y,[2,34]),e(y,[2,35]),e(y,[2,36]),e(y,[2,37]),e(kt,[2,46]),e(kt,[2,47]),e(y,[2,15]),e(y,[2,19]),e(ee,r,{7:78}),e(y,[2,26]),e(y,[2,27]),{5:[1,79]},{5:[1,80]},{4:l,5:u,8:8,9:10,10:12,11:13,12:14,13:15,16:S,17:p,19:g,21:[1,81],22:E,24:k,25:M,26:P,27:A,28:R,29:I,32:25,33:f,35:O,37:x,38:G,41:Y,45:w,48:U,51:tt,52:Et,53:Tt,54:bt,57:at},e(y,[2,32]),e(y,[2,33]),e(y,[2,21])],defaultActions:{5:[2,1],6:[2,2],47:[2,48],48:[2,49]},parseError:(0,s.eW)(function(c,d){if(d.recoverable)this.trace(c);else{var o=new Error(c);throw o.hash=d,o}},"parseError"),parse:(0,s.eW)(function(c){var d=this,o=[0],_=[],T=[null],a=[],ft=this.table,h="",et=0,nt=0,pt=0,Dt=2,vt=1,we=a.slice.call(arguments,1),D=Object.create(this.lexer),st={yy:{}};for(var It in this.yy)Object.prototype.hasOwnProperty.call(this.yy,It)&&(st.yy[It]=this.yy[It]);D.setInput(c,st.yy),st.yy.lexer=D,st.yy.parser=this,typeof D.yylloc=="undefined"&&(D.yylloc={});var wt=D.yylloc;a.push(wt);var Ne=D.options&&D.options.ranges;typeof st.yy.parseError=="function"?this.parseError=st.yy.parseError:this.parseError=Object.getPrototypeOf(this).parseError;function Pe(N){o.length=o.length-2*N,T.length=T.length-N,a.length=a.length-N}(0,s.eW)(Pe,"popStack");function se(){var N;return N=_.pop()||D.lex()||vt,typeof N!="number"&&(N instanceof Array&&(_=N,N=_.pop()),N=d.symbols_[N]||N),N}(0,s.eW)(se,"lex");for(var L,Nt,it,W,We,Pt,ot={},Ct,j,ie,At;;){if(it=o[o.length-1],this.defaultActions[it]?W=this.defaultActions[it]:((L===null||typeof L=="undefined")&&(L=se()),W=ft[it]&&ft[it][L]),typeof W=="undefined"||!W.length||!W[0]){var Wt="";At=[];for(Ct in ft[it])this.terminals_[Ct]&&Ct>Dt&&At.push("'"+this.terminals_[Ct]+"'");D.showPosition?Wt="Parse error on line "+(et+1)+`:
`+D.showPosition()+`
Expecting `+At.join(", ")+", got '"+(this.terminals_[L]||L)+"'":Wt="Parse error on line "+(et+1)+": Unexpected "+(L==vt?"end of input":"'"+(this.terminals_[L]||L)+"'"),this.parseError(Wt,{text:D.match,token:this.terminals_[L]||L,line:D.yylineno,loc:wt,expected:At})}if(W[0]instanceof Array&&W.length>1)throw new Error("Parse Error: multiple actions possible at state: "+it+", token: "+L);switch(W[0]){case 1:o.push(L),T.push(D.yytext),a.push(D.yylloc),o.push(W[1]),L=null,Nt?(L=Nt,Nt=null):(nt=D.yyleng,h=D.yytext,et=D.yylineno,wt=D.yylloc,pt>0&&pt--);break;case 2:if(j=this.productions_[W[1]][1],ot.$=T[T.length-j],ot._$={first_line:a[a.length-(j||1)].first_line,last_line:a[a.length-1].last_line,first_column:a[a.length-(j||1)].first_column,last_column:a[a.length-1].last_column},Ne&&(ot._$.range=[a[a.length-(j||1)].range[0],a[a.length-1].range[1]]),Pt=this.performAction.apply(ot,[h,nt,et,st.yy,W[1],T,a].concat(we)),typeof Pt!="undefined")return Pt;j&&(o=o.slice(0,-1*j*2),T=T.slice(0,-1*j),a=a.slice(0,-1*j)),o.push(this.productions_[W[1]][0]),T.push(ot.$),a.push(ot._$),ie=ft[o[o.length-2]][o[o.length-1]],o.push(ie);break;case 3:return!0}}return!0},"parse")},Ie=function(){var J={EOF:1,parseError:(0,s.eW)(function(d,o){if(this.yy.parser)this.yy.parser.parseError(d,o);else throw new Error(d)},"parseError"),setInput:(0,s.eW)(function(c,d){return this.yy=d||this.yy||{},this._input=c,this._more=this._backtrack=this.done=!1,this.yylineno=this.yyleng=0,this.yytext=this.matched=this.match="",this.conditionStack=["INITIAL"],this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0},this.options.ranges&&(this.yylloc.range=[0,0]),this.offset=0,this},"setInput"),input:(0,s.eW)(function(){var c=this._input[0];this.yytext+=c,this.yyleng++,this.offset++,this.match+=c,this.matched+=c;var d=c.match(/(?:\r\n?|\n).*/g);return d?(this.yylineno++,this.yylloc.last_line++):this.yylloc.last_column++,this.options.ranges&&this.yylloc.range[1]++,this._input=this._input.slice(1),c},"input"),unput:(0,s.eW)(function(c){var d=c.length,o=c.split(/(?:\r\n?|\n)/g);this._input=c+this._input,this.yytext=this.yytext.substr(0,this.yytext.length-d),this.offset-=d;var _=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1),this.matched=this.matched.substr(0,this.matched.length-1),o.length-1&&(this.yylineno-=o.length-1);var T=this.yylloc.range;return this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:o?(o.length===_.length?this.yylloc.first_column:0)+_[_.length-o.length].length-o[0].length:this.yylloc.first_column-d},this.options.ranges&&(this.yylloc.range=[T[0],T[0]+this.yyleng-d]),this.yyleng=this.yytext.length,this},"unput"),more:(0,s.eW)(function(){return this._more=!0,this},"more"),reject:(0,s.eW)(function(){if(this.options.backtrack_lexer)this._backtrack=!0;else return this.parseError("Lexical error on line "+(this.yylineno+1)+`. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
`+this.showPosition(),{text:"",token:null,line:this.yylineno});return this},"reject"),less:(0,s.eW)(function(c){this.unput(this.match.slice(c))},"less"),pastInput:(0,s.eW)(function(){var c=this.matched.substr(0,this.matched.length-this.match.length);return(c.length>20?"...":"")+c.substr(-20).replace(/\n/g,"")},"pastInput"),upcomingInput:(0,s.eW)(function(){var c=this.match;return c.length<20&&(c+=this._input.substr(0,20-c.length)),(c.substr(0,20)+(c.length>20?"...":"")).replace(/\n/g,"")},"upcomingInput"),showPosition:(0,s.eW)(function(){var c=this.pastInput(),d=new Array(c.length+1).join("-");return c+this.upcomingInput()+`
`+d+"^"},"showPosition"),test_match:(0,s.eW)(function(c,d){var o,_,T;if(this.options.backtrack_lexer&&(T={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done},this.options.ranges&&(T.yylloc.range=this.yylloc.range.slice(0))),_=c[0].match(/(?:\r\n?|\n).*/g),_&&(this.yylineno+=_.length),this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:_?_[_.length-1].length-_[_.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+c[0].length},this.yytext+=c[0],this.match+=c[0],this.matches=c,this.yyleng=this.yytext.length,this.options.ranges&&(this.yylloc.range=[this.offset,this.offset+=this.yyleng]),this._more=!1,this._backtrack=!1,this._input=this._input.slice(c[0].length),this.matched+=c[0],o=this.performAction.call(this,this.yy,this,d,this.conditionStack[this.conditionStack.length-1]),this.done&&this._input&&(this.done=!1),o)return o;if(this._backtrack){for(var a in T)this[a]=T[a];return!1}return!1},"test_match"),next:(0,s.eW)(function(){if(this.done)return this.EOF;this._input||(this.done=!0);var c,d,o,_;this._more||(this.yytext="",this.match="");for(var T=this._currentRules(),a=0;a<T.length;a++)if(o=this._input.match(this.rules[T[a]]),o&&(!d||o[0].length>d[0].length)){if(d=o,_=a,this.options.backtrack_lexer){if(c=this.test_match(o,T[a]),c!==!1)return c;if(this._backtrack){d=!1;continue}else return!1}else if(!this.options.flex)break}return d?(c=this.test_match(d,T[_]),c!==!1?c:!1):this._input===""?this.EOF:this.parseError("Lexical error on line "+(this.yylineno+1)+`. Unrecognized text.
`+this.showPosition(),{text:"",token:null,line:this.yylineno})},"next"),lex:(0,s.eW)(function(){var d=this.next();return d||this.lex()},"lex"),begin:(0,s.eW)(function(d){this.conditionStack.push(d)},"begin"),popState:(0,s.eW)(function(){var d=this.conditionStack.length-1;return d>0?this.conditionStack.pop():this.conditionStack[0]},"popState"),_currentRules:(0,s.eW)(function(){return this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]?this.conditions[this.conditionStack[this.conditionStack.length-1]].rules:this.conditions.INITIAL.rules},"_currentRules"),topState:(0,s.eW)(function(d){return d=this.conditionStack.length-1-Math.abs(d||0),d>=0?this.conditionStack[d]:"INITIAL"},"topState"),pushState:(0,s.eW)(function(d){this.begin(d)},"pushState"),stateStackSize:(0,s.eW)(function(){return this.conditionStack.length},"stateStackSize"),options:{"case-insensitive":!0},performAction:(0,s.eW)(function(d,o,_,T){var a=T;switch(_){case 0:return 38;case 1:return 40;case 2:return 39;case 3:return 44;case 4:return 51;case 5:return 52;case 6:return 53;case 7:return 54;case 8:break;case 9:break;case 10:return 5;case 11:break;case 12:break;case 13:break;case 14:break;case 15:return this.pushState("SCALE"),17;break;case 16:return 18;case 17:this.popState();break;case 18:return this.begin("acc_title"),33;break;case 19:return this.popState(),"acc_title_value";break;case 20:return this.begin("acc_descr"),35;break;case 21:return this.popState(),"acc_descr_value";break;case 22:this.begin("acc_descr_multiline");break;case 23:this.popState();break;case 24:return"acc_descr_multiline_value";case 25:return this.pushState("CLASSDEF"),41;break;case 26:return this.popState(),this.pushState("CLASSDEFID"),"DEFAULT_CLASSDEF_ID";break;case 27:return this.popState(),this.pushState("CLASSDEFID"),42;break;case 28:return this.popState(),43;break;case 29:return this.pushState("CLASS"),48;break;case 30:return this.popState(),this.pushState("CLASS_STYLE"),49;break;case 31:return this.popState(),50;break;case 32:return this.pushState("STYLE"),45;break;case 33:return this.popState(),this.pushState("STYLEDEF_STYLES"),46;break;case 34:return this.popState(),47;break;case 35:return this.pushState("SCALE"),17;break;case 36:return 18;case 37:this.popState();break;case 38:this.pushState("STATE");break;case 39:return this.popState(),o.yytext=o.yytext.slice(0,-8).trim(),25;break;case 40:return this.popState(),o.yytext=o.yytext.slice(0,-8).trim(),26;break;case 41:return this.popState(),o.yytext=o.yytext.slice(0,-10).trim(),27;break;case 42:return this.popState(),o.yytext=o.yytext.slice(0,-8).trim(),25;break;case 43:return this.popState(),o.yytext=o.yytext.slice(0,-8).trim(),26;break;case 44:return this.popState(),o.yytext=o.yytext.slice(0,-10).trim(),27;break;case 45:return 51;case 46:return 52;case 47:return 53;case 48:return 54;case 49:this.pushState("STATE_STRING");break;case 50:return this.pushState("STATE_ID"),"AS";break;case 51:return this.popState(),"ID";break;case 52:this.popState();break;case 53:return"STATE_DESCR";case 54:return 19;case 55:this.popState();break;case 56:return this.popState(),this.pushState("struct"),20;break;case 57:break;case 58:return this.popState(),21;break;case 59:break;case 60:return this.begin("NOTE"),29;break;case 61:return this.popState(),this.pushState("NOTE_ID"),59;break;case 62:return this.popState(),this.pushState("NOTE_ID"),60;break;case 63:this.popState(),this.pushState("FLOATING_NOTE");break;case 64:return this.popState(),this.pushState("FLOATING_NOTE_ID"),"AS";break;case 65:break;case 66:return"NOTE_TEXT";case 67:return this.popState(),"ID";break;case 68:return this.popState(),this.pushState("NOTE_TEXT"),24;break;case 69:return this.popState(),o.yytext=o.yytext.substr(2).trim(),31;break;case 70:return this.popState(),o.yytext=o.yytext.slice(0,-8).trim(),31;break;case 71:return 6;case 72:return 6;case 73:return 16;case 74:return 57;case 75:return 24;case 76:return o.yytext=o.yytext.trim(),14;break;case 77:return 15;case 78:return 28;case 79:return 58;case 80:return 5;case 81:return"INVALID"}},"anonymous"),rules:[/^(?:click\b)/i,/^(?:href\b)/i,/^(?:"[^"]*")/i,/^(?:default\b)/i,/^(?:.*direction\s+TB[^\n]*)/i,/^(?:.*direction\s+BT[^\n]*)/i,/^(?:.*direction\s+RL[^\n]*)/i,/^(?:.*direction\s+LR[^\n]*)/i,/^(?:%%(?!\{)[^\n]*)/i,/^(?:[^\}]%%[^\n]*)/i,/^(?:[\n]+)/i,/^(?:[\s]+)/i,/^(?:((?!\n)\s)+)/i,/^(?:#[^\n]*)/i,/^(?:%[^\n]*)/i,/^(?:scale\s+)/i,/^(?:\d+)/i,/^(?:\s+width\b)/i,/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:classDef\s+)/i,/^(?:DEFAULT\s+)/i,/^(?:\w+\s+)/i,/^(?:[^\n]*)/i,/^(?:class\s+)/i,/^(?:(\w+)+((,\s*\w+)*))/i,/^(?:[^\n]*)/i,/^(?:style\s+)/i,/^(?:[\w,]+\s+)/i,/^(?:[^\n]*)/i,/^(?:scale\s+)/i,/^(?:\d+)/i,/^(?:\s+width\b)/i,/^(?:state\s+)/i,/^(?:.*<<fork>>)/i,/^(?:.*<<join>>)/i,/^(?:.*<<choice>>)/i,/^(?:.*\[\[fork\]\])/i,/^(?:.*\[\[join\]\])/i,/^(?:.*\[\[choice\]\])/i,/^(?:.*direction\s+TB[^\n]*)/i,/^(?:.*direction\s+BT[^\n]*)/i,/^(?:.*direction\s+RL[^\n]*)/i,/^(?:.*direction\s+LR[^\n]*)/i,/^(?:["])/i,/^(?:\s*as\s+)/i,/^(?:[^\n\{]*)/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:[^\n\s\{]+)/i,/^(?:\n)/i,/^(?:\{)/i,/^(?:%%(?!\{)[^\n]*)/i,/^(?:\})/i,/^(?:[\n])/i,/^(?:note\s+)/i,/^(?:left of\b)/i,/^(?:right of\b)/i,/^(?:")/i,/^(?:\s*as\s*)/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:[^\n]*)/i,/^(?:\s*[^:\n\s\-]+)/i,/^(?:\s*:[^:\n;]+)/i,/^(?:[\s\S]*?end note\b)/i,/^(?:stateDiagram\s+)/i,/^(?:stateDiagram-v2\s+)/i,/^(?:hide empty description\b)/i,/^(?:\[\*\])/i,/^(?:[^:\n\s\-\{]+)/i,/^(?:\s*:[^:\n;]+)/i,/^(?:-->)/i,/^(?:--)/i,/^(?::::)/i,/^(?:$)/i,/^(?:.)/i],conditions:{LINE:{rules:[12,13],inclusive:!1},struct:{rules:[12,13,25,29,32,38,45,46,47,48,57,58,59,60,74,75,76,77,78],inclusive:!1},FLOATING_NOTE_ID:{rules:[67],inclusive:!1},FLOATING_NOTE:{rules:[64,65,66],inclusive:!1},NOTE_TEXT:{rules:[69,70],inclusive:!1},NOTE_ID:{rules:[68],inclusive:!1},NOTE:{rules:[61,62,63],inclusive:!1},STYLEDEF_STYLEOPTS:{rules:[],inclusive:!1},STYLEDEF_STYLES:{rules:[34],inclusive:!1},STYLE_IDS:{rules:[],inclusive:!1},STYLE:{rules:[33],inclusive:!1},CLASS_STYLE:{rules:[31],inclusive:!1},CLASS:{rules:[30],inclusive:!1},CLASSDEFID:{rules:[28],inclusive:!1},CLASSDEF:{rules:[26,27],inclusive:!1},acc_descr_multiline:{rules:[23,24],inclusive:!1},acc_descr:{rules:[21],inclusive:!1},acc_title:{rules:[19],inclusive:!1},SCALE:{rules:[16,17,36,37],inclusive:!1},ALIAS:{rules:[],inclusive:!1},STATE_ID:{rules:[51],inclusive:!1},STATE_STRING:{rules:[52,53],inclusive:!1},FORK_STATE:{rules:[],inclusive:!1},STATE:{rules:[12,13,39,40,41,42,43,44,49,50,54,55,56],inclusive:!1},ID:{rules:[12,13],inclusive:!1},INITIAL:{rules:[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,18,20,22,25,29,32,35,38,56,60,71,72,73,74,75,76,77,79,80,81],inclusive:!0}}};return J}();Rt.lexer=Ie;function mt(){this.yy={}}return(0,s.eW)(mt,"Parser"),mt.prototype=Rt,Rt.Parser=mt,new mt}();b.parser=b;var v=b,V="TB",H="TB",ct="dir",K="state",z="root",rt="relation",ae="classDef",ne="style",oe="applyClass",lt="default",$t="divider",Mt="fill:none",Bt="fill: #333",Yt="c",Ft="text",Vt="normal",xt="rect",Lt="rectWithTitle",ce="stateStart",le="stateEnd",Gt="divider",Ut="roundedWithTitle",he="note",ue="noteGroup",ht="statediagram",de="state",fe=`${ht}-${de}`,jt="transition",pe="note",Se="note-edge",ye=`${jt} ${Se}`,_e=`${ht}-${pe}`,ge="cluster",Ee=`${ht}-${ge}`,Te="cluster-alt",be=`${ht}-${Te}`,Ht="parent",Kt="note",ke="state",Ot="----",me=`${Ot}${Kt}`,zt=`${Ot}${Ht}`,Xt=(0,s.eW)((e,t=H)=>{if(!e.doc)return t;let i=t;for(const n of e.doc)n.stmt==="dir"&&(i=n.value);return i},"getDir"),De=(0,s.eW)(function(e,t){return t.db.getClasses()},"getClasses"),ve=(0,s.eW)(function(e,t,i,n){return re(this,null,function*(){var E,k;s.cM.info("REF0:"),s.cM.info("Drawing state diagram (v2)",t);const{securityLevel:r,state:l,layout:u}=(0,s.nV)();n.db.extract(n.db.getRootDocV2());const S=n.db.getData(),p=(0,$.q)(t,r);S.type=n.type,S.layoutAlgorithm=u,S.nodeSpacing=(l==null?void 0:l.nodeSpacing)||50,S.rankSpacing=(l==null?void 0:l.rankSpacing)||50,S.markers=["barb"],S.diagramId=t,yield(0,Z.sY)(S,p);const g=8;try{(typeof n.db.getLinks=="function"?n.db.getLinks():new Map).forEach((P,A)=>{var Y;const R=typeof A=="string"?A:typeof(A==null?void 0:A.id)=="string"?A.id:"";if(!R){s.cM.warn("\u26A0\uFE0F Invalid or missing stateId from key:",JSON.stringify(A));return}const I=(Y=p.node())==null?void 0:Y.querySelectorAll("g");let f;if(I==null||I.forEach(w=>{var tt;((tt=w.textContent)==null?void 0:tt.trim())===R&&(f=w)}),!f){s.cM.warn("\u26A0\uFE0F Could not find node matching text:",R);return}const O=f.parentNode;if(!O){s.cM.warn("\u26A0\uFE0F Node has no parent, cannot wrap:",R);return}const x=document.createElementNS("http://www.w3.org/2000/svg","a"),G=P.url.replace(/^"+|"+$/g,"");if(x.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",G),x.setAttribute("target","_blank"),P.tooltip){const w=P.tooltip.replace(/^"+|"+$/g,"");x.setAttribute("title",w)}O.replaceChild(x,f),x.appendChild(f),s.cM.info("\u{1F517} Wrapped node in <a> tag for:",R,P.url)})}catch(M){s.cM.error("\u274C Error injecting clickable links:",M)}F.w8.insertTitle(p,"statediagramTitleText",(E=l==null?void 0:l.titleTopMargin)!=null?E:25,n.db.getDiagramTitle()),(0,B.j)(p,g,ht,(k=l==null?void 0:l.useMaxWidth)!=null?k:!0)})},"draw"),Ce={getClasses:De,draw:ve,getDir:Xt},yt=new Map,X=0;function _t(e="",t=0,i="",n=Ot){const r=i!==null&&i.length>0?`${n}${i}`:"";return`${ke}-${e}${r}-${t}`}(0,s.eW)(_t,"stateDomId");var Ae=(0,s.eW)((e,t,i,n,r,l,u,S)=>{s.cM.trace("items",t),t.forEach(p=>{var g;switch(p.stmt){case K:dt(e,p,i,n,r,l,u,S);break;case lt:dt(e,p,i,n,r,l,u,S);break;case rt:{dt(e,p.state1,i,n,r,l,u,S),dt(e,p.state2,i,n,r,l,u,S);const E={id:"edge"+X,start:p.state1.id,end:p.state2.id,arrowhead:"normal",arrowTypeEnd:"arrow_barb",style:Mt,labelStyle:"",label:s.SY.sanitizeText((g=p.description)!=null?g:"",(0,s.nV)()),arrowheadStyle:Bt,labelpos:Yt,labelType:Ft,thickness:Vt,classes:jt,look:u};r.push(E),X++}break}})},"setupDoc"),Jt=(0,s.eW)((e,t=H)=>{let i=t;if(e.doc)for(const n of e.doc)n.stmt==="dir"&&(i=n.value);return i},"getDir");function ut(e,t,i){if(!t.id||t.id==="</join></fork>"||t.id==="</choice>")return;t.cssClasses&&(Array.isArray(t.cssCompiledStyles)||(t.cssCompiledStyles=[]),t.cssClasses.split(" ").forEach(r=>{var u;const l=i.get(r);l&&(t.cssCompiledStyles=[...(u=t.cssCompiledStyles)!=null?u:[],...l.styles])}));const n=e.find(r=>r.id===t.id);n?Object.assign(n,t):e.push(t)}(0,s.eW)(ut,"insertOrUpdateNode");function Qt(e){var t,i;return(i=(t=e==null?void 0:e.classes)==null?void 0:t.join(" "))!=null?i:""}(0,s.eW)(Qt,"getClassesFromDbInfo");function Zt(e){var t;return(t=e==null?void 0:e.styles)!=null?t:[]}(0,s.eW)(Zt,"getStylesFromDbInfo");var dt=(0,s.eW)((e,t,i,n,r,l,u,S)=>{var P,A,R;const p=t.id,g=i.get(p),E=Qt(g),k=Zt(g),M=(0,s.nV)();if(s.cM.info("dataFetcher parsedItem",t,g,k),p!=="root"){let I=xt;t.start===!0?I=ce:t.start===!1&&(I=le),t.type!==lt&&(I=t.type),yt.get(p)||yt.set(p,{id:p,shape:I,description:s.SY.sanitizeText(p,M),cssClasses:`${E} ${fe}`,cssStyles:k});const f=yt.get(p);t.description&&(Array.isArray(f.description)?(f.shape=Lt,f.description.push(t.description)):(P=f.description)!=null&&P.length&&f.description.length>0?(f.shape=Lt,f.description===p?f.description=[t.description]:f.description=[f.description,t.description]):(f.shape=xt,f.description=t.description),f.description=s.SY.sanitizeTextOrArray(f.description,M)),((A=f.description)==null?void 0:A.length)===1&&f.shape===Lt&&(f.type==="group"?f.shape=Ut:f.shape=xt),!f.type&&t.doc&&(s.cM.info("Setting cluster for XCX",p,Jt(t)),f.type="group",f.isGroup=!0,f.dir=Jt(t),f.shape=t.type===$t?Gt:Ut,f.cssClasses=`${f.cssClasses} ${Ee} ${l?be:""}`);const O={labelStyle:"",shape:f.shape,label:f.description,cssClasses:f.cssClasses,cssCompiledStyles:[],cssStyles:f.cssStyles,id:p,dir:f.dir,domId:_t(p,X),type:f.type,isGroup:f.type==="group",padding:8,rx:10,ry:10,look:u};if(O.shape===Gt&&(O.label=""),e&&e.id!=="root"&&(s.cM.trace("Setting node ",p," to be child of its parent ",e.id),O.parentId=e.id),O.centerLabel=!0,t.note){const x={labelStyle:"",shape:he,label:t.note.text,cssClasses:_e,cssStyles:[],cssCompiledStyles:[],id:p+me+"-"+X,domId:_t(p,X,Kt),type:f.type,isGroup:f.type==="group",padding:(R=M.flowchart)==null?void 0:R.padding,look:u,position:t.note.position},G=p+zt,Y={labelStyle:"",shape:ue,label:t.note.text,cssClasses:f.cssClasses,cssStyles:[],id:p+zt,domId:_t(p,X,Ht),type:"group",isGroup:!0,padding:16,look:u,position:t.note.position};X++,Y.id=G,x.parentId=G,ut(n,Y,S),ut(n,x,S),ut(n,O,S);let w=p,U=x.id;t.note.position==="left of"&&(w=x.id,U=p),r.push({id:w+"-"+U,start:w,end:U,arrowhead:"none",arrowTypeEnd:"",style:Mt,labelStyle:"",classes:ye,arrowheadStyle:Bt,labelpos:Yt,labelType:Ft,thickness:Vt,look:u})}else ut(n,O,S)}t.doc&&(s.cM.trace("Adding nodes children "),Ae(t,t.doc,i,n,r,!l,u,S))},"dataFetcher"),xe=(0,s.eW)(()=>{yt.clear(),X=0},"reset"),C={START_NODE:"[*]",START_TYPE:"start",END_NODE:"[*]",END_TYPE:"end",COLOR_KEYWORD:"color",FILL_KEYWORD:"fill",BG_FILL:"bgFill",STYLECLASS_SEP:","},qt=(0,s.eW)(()=>new Map,"newClassesList"),te=(0,s.eW)(()=>({relations:[],states:new Map,documents:{}}),"newDoc"),gt=(0,s.eW)(e=>JSON.parse(JSON.stringify(e)),"clone"),Le=(q=class{constructor(t){this.version=t,this.nodes=[],this.edges=[],this.rootDoc=[],this.classes=qt(),this.documents={root:te()},this.currentDocument=this.documents.root,this.startEndCount=0,this.dividerCnt=0,this.links=new Map,this.getAccTitle=s.eu,this.setAccTitle=s.GN,this.getAccDescription=s.Mx,this.setAccDescription=s.U$,this.setDiagramTitle=s.g2,this.getDiagramTitle=s.Kr,this.clear(),this.setRootDoc=this.setRootDoc.bind(this),this.getDividerId=this.getDividerId.bind(this),this.setDirection=this.setDirection.bind(this),this.trimColon=this.trimColon.bind(this)}extract(t){this.clear(!0);for(const r of Array.isArray(t)?t:t.doc)switch(r.stmt){case K:this.addState(r.id.trim(),r.type,r.doc,r.description,r.note);break;case rt:this.addRelation(r.state1,r.state2,r.description);break;case ae:this.addStyleClass(r.id.trim(),r.classes);break;case ne:this.handleStyleDef(r);break;case oe:this.setCssClass(r.id.trim(),r.styleClass);break;case"click":this.addLink(r.id,r.url,r.tooltip);break}const i=this.getStates(),n=(0,s.nV)();xe(),dt(void 0,this.getRootDocV2(),i,this.nodes,this.edges,!0,n.look,this.classes);for(const r of this.nodes)if(Array.isArray(r.label)){if(r.description=r.label.slice(1),r.isGroup&&r.description.length>0)throw new Error(`Group nodes can only have label. Remove the additional description for node [${r.id}]`);r.label=r.label[0]}}handleStyleDef(t){const i=t.id.trim().split(","),n=t.styleClass.split(",");for(const r of i){let l=this.getState(r);if(!l){const u=r.trim();this.addState(u),l=this.getState(u)}l&&(l.styles=n.map(u=>{var S;return(S=u.replace(/;/g,""))==null?void 0:S.trim()}))}}setRootDoc(t){s.cM.info("Setting root doc",t),this.rootDoc=t,this.version===1?this.extract(t):this.extract(this.getRootDocV2())}docTranslator(t,i,n){if(i.stmt===rt){this.docTranslator(t,i.state1,!0),this.docTranslator(t,i.state2,!1);return}if(i.stmt===K&&(i.id===C.START_NODE?(i.id=t.id+(n?"_start":"_end"),i.start=n):i.id=i.id.trim()),i.stmt!==z&&i.stmt!==K||!i.doc)return;const r=[];let l=[];for(const u of i.doc)if(u.type===$t){const S=gt(u);S.doc=gt(l),r.push(S),l=[]}else l.push(u);if(r.length>0&&l.length>0){const u={stmt:K,id:(0,F.Ox)(),type:"divider",doc:gt(l)};r.push(gt(u)),i.doc=r}i.doc.forEach(u=>this.docTranslator(i,u,!0))}getRootDocV2(){return this.docTranslator({id:z,stmt:z},{id:z,stmt:z,doc:this.rootDoc},!0),{id:z,doc:this.rootDoc}}addState(t,i=lt,n=void 0,r=void 0,l=void 0,u=void 0,S=void 0,p=void 0){const g=t==null?void 0:t.trim();if(!this.currentDocument.states.has(g))s.cM.info("Adding state ",g,r),this.currentDocument.states.set(g,{stmt:K,id:g,descriptions:[],type:i,doc:n,note:l,classes:[],styles:[],textStyles:[]});else{const E=this.currentDocument.states.get(g);if(!E)throw new Error(`State not found: ${g}`);E.doc||(E.doc=n),E.type||(E.type=i)}if(r&&(s.cM.info("Setting state description",g,r),(Array.isArray(r)?r:[r]).forEach(k=>this.addDescription(g,k.trim()))),l){const E=this.currentDocument.states.get(g);if(!E)throw new Error(`State not found: ${g}`);E.note=l,E.note.text=s.SY.sanitizeText(E.note.text,(0,s.nV)())}u&&(s.cM.info("Setting state classes",g,u),(Array.isArray(u)?u:[u]).forEach(k=>this.setCssClass(g,k.trim()))),S&&(s.cM.info("Setting state styles",g,S),(Array.isArray(S)?S:[S]).forEach(k=>this.setStyle(g,k.trim()))),p&&(s.cM.info("Setting state styles",g,S),(Array.isArray(p)?p:[p]).forEach(k=>this.setTextStyle(g,k.trim())))}clear(t){this.nodes=[],this.edges=[],this.documents={root:te()},this.currentDocument=this.documents.root,this.startEndCount=0,this.classes=qt(),t||(this.links=new Map,(0,s.ZH)())}getState(t){return this.currentDocument.states.get(t)}getStates(){return this.currentDocument.states}logDocuments(){s.cM.info("Documents = ",this.documents)}getRelations(){return this.currentDocument.relations}addLink(t,i,n){this.links.set(t,{url:i,tooltip:n}),s.cM.warn("Adding link",t,i,n)}getLinks(){return this.links}startIdIfNeeded(t=""){return t===C.START_NODE?(this.startEndCount++,`${C.START_TYPE}${this.startEndCount}`):t}startTypeIfNeeded(t="",i=lt){return t===C.START_NODE?C.START_TYPE:i}endIdIfNeeded(t=""){return t===C.END_NODE?(this.startEndCount++,`${C.END_TYPE}${this.startEndCount}`):t}endTypeIfNeeded(t="",i=lt){return t===C.END_NODE?C.END_TYPE:i}addRelationObjs(t,i,n=""){const r=this.startIdIfNeeded(t.id.trim()),l=this.startTypeIfNeeded(t.id.trim(),t.type),u=this.startIdIfNeeded(i.id.trim()),S=this.startTypeIfNeeded(i.id.trim(),i.type);this.addState(r,l,t.doc,t.description,t.note,t.classes,t.styles,t.textStyles),this.addState(u,S,i.doc,i.description,i.note,i.classes,i.styles,i.textStyles),this.currentDocument.relations.push({id1:r,id2:u,relationTitle:s.SY.sanitizeText(n,(0,s.nV)())})}addRelation(t,i,n){if(typeof t=="object"&&typeof i=="object")this.addRelationObjs(t,i,n);else if(typeof t=="string"&&typeof i=="string"){const r=this.startIdIfNeeded(t.trim()),l=this.startTypeIfNeeded(t),u=this.endIdIfNeeded(i.trim()),S=this.endTypeIfNeeded(i);this.addState(r,l),this.addState(u,S),this.currentDocument.relations.push({id1:r,id2:u,relationTitle:n?s.SY.sanitizeText(n,(0,s.nV)()):void 0})}}addDescription(t,i){var l;const n=this.currentDocument.states.get(t),r=i.startsWith(":")?i.replace(":","").trim():i;(l=n==null?void 0:n.descriptions)==null||l.push(s.SY.sanitizeText(r,(0,s.nV)()))}cleanupLabel(t){return t.startsWith(":")?t.slice(2).trim():t.trim()}getDividerId(){return this.dividerCnt++,`divider-id-${this.dividerCnt}`}addStyleClass(t,i=""){this.classes.has(t)||this.classes.set(t,{id:t,styles:[],textStyles:[]});const n=this.classes.get(t);i&&n&&i.split(C.STYLECLASS_SEP).forEach(r=>{const l=r.replace(/([^;]*);/,"$1").trim();if(RegExp(C.COLOR_KEYWORD).exec(r)){const S=l.replace(C.FILL_KEYWORD,C.BG_FILL).replace(C.COLOR_KEYWORD,C.FILL_KEYWORD);n.textStyles.push(S)}n.styles.push(l)})}getClasses(){return this.classes}setCssClass(t,i){t.split(",").forEach(n=>{var l;let r=this.getState(n);if(!r){const u=n.trim();this.addState(u),r=this.getState(u)}(l=r==null?void 0:r.classes)==null||l.push(i)})}setStyle(t,i){var n,r;(r=(n=this.getState(t))==null?void 0:n.styles)==null||r.push(i)}setTextStyle(t,i){var n,r;(r=(n=this.getState(t))==null?void 0:n.textStyles)==null||r.push(i)}getDirectionStatement(){return this.rootDoc.find(t=>t.stmt===ct)}getDirection(){var t,i;return(i=(t=this.getDirectionStatement())==null?void 0:t.value)!=null?i:V}setDirection(t){const i=this.getDirectionStatement();i?i.value=t:this.rootDoc.unshift({stmt:ct,value:t})}trimColon(t){return t.startsWith(":")?t.slice(1).trim():t.trim()}getData(){const t=(0,s.nV)();return{nodes:this.nodes,edges:this.edges,other:{},config:t,direction:Xt(this.getRootDocV2())}}getConfig(){return(0,s.nV)().state}},(0,s.eW)(q,"StateDB"),q.relationType={AGGREGATION:0,EXTENSION:1,COMPOSITION:2,DEPENDENCY:3},q),Oe=(0,s.eW)(e=>`
defs #statediagram-barbEnd {
    fill: ${e.transitionColor};
    stroke: ${e.transitionColor};
  }
g.stateGroup text {
  fill: ${e.nodeBorder};
  stroke: none;
  font-size: 10px;
}
g.stateGroup text {
  fill: ${e.textColor};
  stroke: none;
  font-size: 10px;

}
g.stateGroup .state-title {
  font-weight: bolder;
  fill: ${e.stateLabelColor};
}

g.stateGroup rect {
  fill: ${e.mainBkg};
  stroke: ${e.nodeBorder};
}

g.stateGroup line {
  stroke: ${e.lineColor};
  stroke-width: 1;
}

.transition {
  stroke: ${e.transitionColor};
  stroke-width: 1;
  fill: none;
}

.stateGroup .composit {
  fill: ${e.background};
  border-bottom: 1px
}

.stateGroup .alt-composit {
  fill: #e0e0e0;
  border-bottom: 1px
}

.state-note {
  stroke: ${e.noteBorderColor};
  fill: ${e.noteBkgColor};

  text {
    fill: ${e.noteTextColor};
    stroke: none;
    font-size: 10px;
  }
}

.stateLabel .box {
  stroke: none;
  stroke-width: 0;
  fill: ${e.mainBkg};
  opacity: 0.5;
}

.edgeLabel .label rect {
  fill: ${e.labelBackgroundColor};
  opacity: 0.5;
}
.edgeLabel {
  background-color: ${e.edgeLabelBackground};
  p {
    background-color: ${e.edgeLabelBackground};
  }
  rect {
    opacity: 0.5;
    background-color: ${e.edgeLabelBackground};
    fill: ${e.edgeLabelBackground};
  }
  text-align: center;
}
.edgeLabel .label text {
  fill: ${e.transitionLabelColor||e.tertiaryTextColor};
}
.label div .edgeLabel {
  color: ${e.transitionLabelColor||e.tertiaryTextColor};
}

.stateLabel text {
  fill: ${e.stateLabelColor};
  font-size: 10px;
  font-weight: bold;
}

.node circle.state-start {
  fill: ${e.specialStateColor};
  stroke: ${e.specialStateColor};
}

.node .fork-join {
  fill: ${e.specialStateColor};
  stroke: ${e.specialStateColor};
}

.node circle.state-end {
  fill: ${e.innerEndBackground};
  stroke: ${e.background};
  stroke-width: 1.5
}
.end-state-inner {
  fill: ${e.compositeBackground||e.background};
  // stroke: ${e.background};
  stroke-width: 1.5
}

.node rect {
  fill: ${e.stateBkg||e.mainBkg};
  stroke: ${e.stateBorder||e.nodeBorder};
  stroke-width: 1px;
}
.node polygon {
  fill: ${e.mainBkg};
  stroke: ${e.stateBorder||e.nodeBorder};;
  stroke-width: 1px;
}
#statediagram-barbEnd {
  fill: ${e.lineColor};
}

.statediagram-cluster rect {
  fill: ${e.compositeTitleBackground};
  stroke: ${e.stateBorder||e.nodeBorder};
  stroke-width: 1px;
}

.cluster-label, .nodeLabel {
  color: ${e.stateLabelColor};
  // line-height: 1;
}

.statediagram-cluster rect.outer {
  rx: 5px;
  ry: 5px;
}
.statediagram-state .divider {
  stroke: ${e.stateBorder||e.nodeBorder};
}

.statediagram-state .title-state {
  rx: 5px;
  ry: 5px;
}
.statediagram-cluster.statediagram-cluster .inner {
  fill: ${e.compositeBackground||e.background};
}
.statediagram-cluster.statediagram-cluster-alt .inner {
  fill: ${e.altBackground?e.altBackground:"#efefef"};
}

.statediagram-cluster .inner {
  rx:0;
  ry:0;
}

.statediagram-state rect.basic {
  rx: 5px;
  ry: 5px;
}
.statediagram-state rect.divider {
  stroke-dasharray: 10,10;
  fill: ${e.altBackground?e.altBackground:"#efefef"};
}

.note-edge {
  stroke-dasharray: 5;
}

.statediagram-note rect {
  fill: ${e.noteBkgColor};
  stroke: ${e.noteBorderColor};
  stroke-width: 1px;
  rx: 0;
  ry: 0;
}
.statediagram-note rect {
  fill: ${e.noteBkgColor};
  stroke: ${e.noteBorderColor};
  stroke-width: 1px;
  rx: 0;
  ry: 0;
}

.statediagram-note text {
  fill: ${e.noteTextColor};
}

.statediagram-note .nodeLabel {
  color: ${e.noteTextColor};
}
.statediagram .edgeLabel {
  color: red; // ${e.noteTextColor};
}

#dependencyStart, #dependencyEnd {
  fill: ${e.lineColor};
  stroke: ${e.lineColor};
  stroke-width: 1;
}

.statediagramTitleText {
  text-anchor: middle;
  font-size: 18px;
  fill: ${e.textColor};
}
`,"getStyles"),Re=Oe},88589:function(St,Q,m){m.d(Q,{j:function(){return B}});var $=m(32426),B=(0,$.eW)((s,b,v,V)=>{s.attr("class",v);const{width:H,height:ct,x:K,y:z}=Z(s,b);(0,$.v2)(s,ct,H,V);const rt=F(K,z,H,ct,b);s.attr("viewBox",rt),$.cM.debug(`viewBox configured: ${rt} with padding: ${b}`)},"setupViewPortForSVG"),Z=(0,$.eW)((s,b)=>{var V;const v=((V=s.node())==null?void 0:V.getBBox())||{width:0,height:0,x:0,y:0};return{width:v.width+b*2,height:v.height+b*2,x:v.x,y:v.y}},"calculateDimensionsWithPadding"),F=(0,$.eW)((s,b,v,V,H)=>`${s-H} ${b-H} ${v} ${V}`,"createViewBox")}}]);
}());