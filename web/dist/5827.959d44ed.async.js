"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[5827],{45827:function(Gt,He,U){U.d(He,{diagram:function(){return jt}});var qe=U(8111),s=U(32426),Qe=U(17967),A=U(27484),Je=U(59542),$e=U(10285),et=U(28734),T=U(3466),me=function(){var e=(0,s.eW)(function(W,o,u,f){for(u=u||{},f=W.length;f--;u[W[f]]=o);return u},"o"),r=[6,8,10,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,33,35,36,38,40],a=[1,26],c=[1,27],n=[1,28],y=[1,29],k=[1,30],P=[1,31],Y=[1,32],N=[1,33],C=[1,34],L=[1,9],K=[1,10],V=[1,11],R=[1,12],w=[1,13],re=[1,14],se=[1,15],ie=[1,16],ae=[1,19],ne=[1,20],ce=[1,21],le=[1,22],oe=[1,23],m=[1,25],b=[1,35],v={trace:(0,s.eW)(function(){},"trace"),yy:{},symbols_:{error:2,start:3,gantt:4,document:5,EOF:6,line:7,SPACE:8,statement:9,NL:10,weekday:11,weekday_monday:12,weekday_tuesday:13,weekday_wednesday:14,weekday_thursday:15,weekday_friday:16,weekday_saturday:17,weekday_sunday:18,weekend:19,weekend_friday:20,weekend_saturday:21,dateFormat:22,inclusiveEndDates:23,topAxis:24,axisFormat:25,tickInterval:26,excludes:27,includes:28,todayMarker:29,title:30,acc_title:31,acc_title_value:32,acc_descr:33,acc_descr_value:34,acc_descr_multiline_value:35,section:36,clickStatement:37,taskTxt:38,taskData:39,click:40,callbackname:41,callbackargs:42,href:43,clickStatementDebug:44,$accept:0,$end:1},terminals_:{2:"error",4:"gantt",6:"EOF",8:"SPACE",10:"NL",12:"weekday_monday",13:"weekday_tuesday",14:"weekday_wednesday",15:"weekday_thursday",16:"weekday_friday",17:"weekday_saturday",18:"weekday_sunday",20:"weekend_friday",21:"weekend_saturday",22:"dateFormat",23:"inclusiveEndDates",24:"topAxis",25:"axisFormat",26:"tickInterval",27:"excludes",28:"includes",29:"todayMarker",30:"title",31:"acc_title",32:"acc_title_value",33:"acc_descr",34:"acc_descr_value",35:"acc_descr_multiline_value",36:"section",38:"taskTxt",39:"taskData",40:"click",41:"callbackname",42:"callbackargs",43:"href"},productions_:[0,[3,3],[5,0],[5,2],[7,2],[7,1],[7,1],[7,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[11,1],[19,1],[19,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,1],[9,2],[9,2],[9,1],[9,1],[9,1],[9,2],[37,2],[37,3],[37,3],[37,4],[37,3],[37,4],[37,2],[44,2],[44,3],[44,3],[44,4],[44,3],[44,4],[44,2]],performAction:(0,s.eW)(function(o,u,f,d,g,i,l){var t=i.length-1;switch(g){case 1:return i[t-1];case 2:this.$=[];break;case 3:i[t-1].push(i[t]),this.$=i[t-1];break;case 4:case 5:this.$=i[t];break;case 6:case 7:this.$=[];break;case 8:d.setWeekday("monday");break;case 9:d.setWeekday("tuesday");break;case 10:d.setWeekday("wednesday");break;case 11:d.setWeekday("thursday");break;case 12:d.setWeekday("friday");break;case 13:d.setWeekday("saturday");break;case 14:d.setWeekday("sunday");break;case 15:d.setWeekend("friday");break;case 16:d.setWeekend("saturday");break;case 17:d.setDateFormat(i[t].substr(11)),this.$=i[t].substr(11);break;case 18:d.enableInclusiveEndDates(),this.$=i[t].substr(18);break;case 19:d.TopAxis(),this.$=i[t].substr(8);break;case 20:d.setAxisFormat(i[t].substr(11)),this.$=i[t].substr(11);break;case 21:d.setTickInterval(i[t].substr(13)),this.$=i[t].substr(13);break;case 22:d.setExcludes(i[t].substr(9)),this.$=i[t].substr(9);break;case 23:d.setIncludes(i[t].substr(9)),this.$=i[t].substr(9);break;case 24:d.setTodayMarker(i[t].substr(12)),this.$=i[t].substr(12);break;case 27:d.setDiagramTitle(i[t].substr(6)),this.$=i[t].substr(6);break;case 28:this.$=i[t].trim(),d.setAccTitle(this.$);break;case 29:case 30:this.$=i[t].trim(),d.setAccDescription(this.$);break;case 31:d.addSection(i[t].substr(8)),this.$=i[t].substr(8);break;case 33:d.addTask(i[t-1],i[t]),this.$="task";break;case 34:this.$=i[t-1],d.setClickEvent(i[t-1],i[t],null);break;case 35:this.$=i[t-2],d.setClickEvent(i[t-2],i[t-1],i[t]);break;case 36:this.$=i[t-2],d.setClickEvent(i[t-2],i[t-1],null),d.setLink(i[t-2],i[t]);break;case 37:this.$=i[t-3],d.setClickEvent(i[t-3],i[t-2],i[t-1]),d.setLink(i[t-3],i[t]);break;case 38:this.$=i[t-2],d.setClickEvent(i[t-2],i[t],null),d.setLink(i[t-2],i[t-1]);break;case 39:this.$=i[t-3],d.setClickEvent(i[t-3],i[t-1],i[t]),d.setLink(i[t-3],i[t-2]);break;case 40:this.$=i[t-1],d.setLink(i[t-1],i[t]);break;case 41:case 47:this.$=i[t-1]+" "+i[t];break;case 42:case 43:case 45:this.$=i[t-2]+" "+i[t-1]+" "+i[t];break;case 44:case 46:this.$=i[t-3]+" "+i[t-2]+" "+i[t-1]+" "+i[t];break}},"anonymous"),table:[{3:1,4:[1,2]},{1:[3]},e(r,[2,2],{5:3}),{6:[1,4],7:5,8:[1,6],9:7,10:[1,8],11:17,12:a,13:c,14:n,15:y,16:k,17:P,18:Y,19:18,20:N,21:C,22:L,23:K,24:V,25:R,26:w,27:re,28:se,29:ie,30:ae,31:ne,33:ce,35:le,36:oe,37:24,38:m,40:b},e(r,[2,7],{1:[2,1]}),e(r,[2,3]),{9:36,11:17,12:a,13:c,14:n,15:y,16:k,17:P,18:Y,19:18,20:N,21:C,22:L,23:K,24:V,25:R,26:w,27:re,28:se,29:ie,30:ae,31:ne,33:ce,35:le,36:oe,37:24,38:m,40:b},e(r,[2,5]),e(r,[2,6]),e(r,[2,17]),e(r,[2,18]),e(r,[2,19]),e(r,[2,20]),e(r,[2,21]),e(r,[2,22]),e(r,[2,23]),e(r,[2,24]),e(r,[2,25]),e(r,[2,26]),e(r,[2,27]),{32:[1,37]},{34:[1,38]},e(r,[2,30]),e(r,[2,31]),e(r,[2,32]),{39:[1,39]},e(r,[2,8]),e(r,[2,9]),e(r,[2,10]),e(r,[2,11]),e(r,[2,12]),e(r,[2,13]),e(r,[2,14]),e(r,[2,15]),e(r,[2,16]),{41:[1,40],43:[1,41]},e(r,[2,4]),e(r,[2,28]),e(r,[2,29]),e(r,[2,33]),e(r,[2,34],{42:[1,42],43:[1,43]}),e(r,[2,40],{41:[1,44]}),e(r,[2,35],{43:[1,45]}),e(r,[2,36]),e(r,[2,38],{42:[1,46]}),e(r,[2,37]),e(r,[2,39])],defaultActions:{},parseError:(0,s.eW)(function(o,u){if(u.recoverable)this.trace(o);else{var f=new Error(o);throw f.hash=u,f}},"parseError"),parse:(0,s.eW)(function(o){var u=this,f=[0],d=[],g=[null],i=[],l=this.table,t="",E=0,_=0,x=0,M=2,D=1,Ie=i.slice.call(arguments,1),S=Object.create(this.lexer),Z={yy:{}};for(var Ae in this.yy)Object.prototype.hasOwnProperty.call(this.yy,Ae)&&(Z.yy[Ae]=this.yy[Ae]);S.setInput(o,Z.yy),Z.yy.lexer=S,Z.yy.parser=this,typeof S.yylloc=="undefined"&&(S.yylloc={});var Le=S.yylloc;i.push(Le);var Kt=S.options&&S.options.ranges;typeof Z.yy.parseError=="function"?this.parseError=Z.yy.parseError:this.parseError=Object.getPrototypeOf(this).parseError;function Xt(O){f.length=f.length-2*O,g.length=g.length-O,i.length=i.length-O}(0,s.eW)(Xt,"popStack");function Ge(){var O;return O=d.pop()||S.lex()||D,typeof O!="number"&&(O instanceof Array&&(d=O,O=d.pop()),O=u.symbols_[O]||O),O}(0,s.eW)(Ge,"lex");for(var F,Me,H,B,Zt,Fe,J={},he,X,Ze,ye;;){if(H=f[f.length-1],this.defaultActions[H]?B=this.defaultActions[H]:((F===null||typeof F=="undefined")&&(F=Ge()),B=l[H]&&l[H][F]),typeof B=="undefined"||!B.length||!B[0]){var Pe="";ye=[];for(he in l[H])this.terminals_[he]&&he>M&&ye.push("'"+this.terminals_[he]+"'");S.showPosition?Pe="Parse error on line "+(E+1)+`:
`+S.showPosition()+`
Expecting `+ye.join(", ")+", got '"+(this.terminals_[F]||F)+"'":Pe="Parse error on line "+(E+1)+": Unexpected "+(F==D?"end of input":"'"+(this.terminals_[F]||F)+"'"),this.parseError(Pe,{text:S.match,token:this.terminals_[F]||F,line:S.yylineno,loc:Le,expected:ye})}if(B[0]instanceof Array&&B.length>1)throw new Error("Parse Error: multiple actions possible at state: "+H+", token: "+F);switch(B[0]){case 1:f.push(F),g.push(S.yytext),i.push(S.yylloc),f.push(B[1]),F=null,Me?(F=Me,Me=null):(_=S.yyleng,t=S.yytext,E=S.yylineno,Le=S.yylloc,x>0&&x--);break;case 2:if(X=this.productions_[B[1]][1],J.$=g[g.length-X],J._$={first_line:i[i.length-(X||1)].first_line,last_line:i[i.length-1].last_line,first_column:i[i.length-(X||1)].first_column,last_column:i[i.length-1].last_column},Kt&&(J._$.range=[i[i.length-(X||1)].range[0],i[i.length-1].range[1]]),Fe=this.performAction.apply(J,[t,_,E,Z.yy,B[1],g,i].concat(Ie)),typeof Fe!="undefined")return Fe;X&&(f=f.slice(0,-1*X*2),g=g.slice(0,-1*X),i=i.slice(0,-1*X)),f.push(this.productions_[B[1]][0]),g.push(J.$),i.push(J._$),Ze=l[f[f.length-2]][f[f.length-1]],f.push(Ze);break;case 3:return!0}}return!0},"parse")},p=function(){var W={EOF:1,parseError:(0,s.eW)(function(u,f){if(this.yy.parser)this.yy.parser.parseError(u,f);else throw new Error(u)},"parseError"),setInput:(0,s.eW)(function(o,u){return this.yy=u||this.yy||{},this._input=o,this._more=this._backtrack=this.done=!1,this.yylineno=this.yyleng=0,this.yytext=this.matched=this.match="",this.conditionStack=["INITIAL"],this.yylloc={first_line:1,first_column:0,last_line:1,last_column:0},this.options.ranges&&(this.yylloc.range=[0,0]),this.offset=0,this},"setInput"),input:(0,s.eW)(function(){var o=this._input[0];this.yytext+=o,this.yyleng++,this.offset++,this.match+=o,this.matched+=o;var u=o.match(/(?:\r\n?|\n).*/g);return u?(this.yylineno++,this.yylloc.last_line++):this.yylloc.last_column++,this.options.ranges&&this.yylloc.range[1]++,this._input=this._input.slice(1),o},"input"),unput:(0,s.eW)(function(o){var u=o.length,f=o.split(/(?:\r\n?|\n)/g);this._input=o+this._input,this.yytext=this.yytext.substr(0,this.yytext.length-u),this.offset-=u;var d=this.match.split(/(?:\r\n?|\n)/g);this.match=this.match.substr(0,this.match.length-1),this.matched=this.matched.substr(0,this.matched.length-1),f.length-1&&(this.yylineno-=f.length-1);var g=this.yylloc.range;return this.yylloc={first_line:this.yylloc.first_line,last_line:this.yylineno+1,first_column:this.yylloc.first_column,last_column:f?(f.length===d.length?this.yylloc.first_column:0)+d[d.length-f.length].length-f[0].length:this.yylloc.first_column-u},this.options.ranges&&(this.yylloc.range=[g[0],g[0]+this.yyleng-u]),this.yyleng=this.yytext.length,this},"unput"),more:(0,s.eW)(function(){return this._more=!0,this},"more"),reject:(0,s.eW)(function(){if(this.options.backtrack_lexer)this._backtrack=!0;else return this.parseError("Lexical error on line "+(this.yylineno+1)+`. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
`+this.showPosition(),{text:"",token:null,line:this.yylineno});return this},"reject"),less:(0,s.eW)(function(o){this.unput(this.match.slice(o))},"less"),pastInput:(0,s.eW)(function(){var o=this.matched.substr(0,this.matched.length-this.match.length);return(o.length>20?"...":"")+o.substr(-20).replace(/\n/g,"")},"pastInput"),upcomingInput:(0,s.eW)(function(){var o=this.match;return o.length<20&&(o+=this._input.substr(0,20-o.length)),(o.substr(0,20)+(o.length>20?"...":"")).replace(/\n/g,"")},"upcomingInput"),showPosition:(0,s.eW)(function(){var o=this.pastInput(),u=new Array(o.length+1).join("-");return o+this.upcomingInput()+`
`+u+"^"},"showPosition"),test_match:(0,s.eW)(function(o,u){var f,d,g;if(this.options.backtrack_lexer&&(g={yylineno:this.yylineno,yylloc:{first_line:this.yylloc.first_line,last_line:this.last_line,first_column:this.yylloc.first_column,last_column:this.yylloc.last_column},yytext:this.yytext,match:this.match,matches:this.matches,matched:this.matched,yyleng:this.yyleng,offset:this.offset,_more:this._more,_input:this._input,yy:this.yy,conditionStack:this.conditionStack.slice(0),done:this.done},this.options.ranges&&(g.yylloc.range=this.yylloc.range.slice(0))),d=o[0].match(/(?:\r\n?|\n).*/g),d&&(this.yylineno+=d.length),this.yylloc={first_line:this.yylloc.last_line,last_line:this.yylineno+1,first_column:this.yylloc.last_column,last_column:d?d[d.length-1].length-d[d.length-1].match(/\r?\n?/)[0].length:this.yylloc.last_column+o[0].length},this.yytext+=o[0],this.match+=o[0],this.matches=o,this.yyleng=this.yytext.length,this.options.ranges&&(this.yylloc.range=[this.offset,this.offset+=this.yyleng]),this._more=!1,this._backtrack=!1,this._input=this._input.slice(o[0].length),this.matched+=o[0],f=this.performAction.call(this,this.yy,this,u,this.conditionStack[this.conditionStack.length-1]),this.done&&this._input&&(this.done=!1),f)return f;if(this._backtrack){for(var i in g)this[i]=g[i];return!1}return!1},"test_match"),next:(0,s.eW)(function(){if(this.done)return this.EOF;this._input||(this.done=!0);var o,u,f,d;this._more||(this.yytext="",this.match="");for(var g=this._currentRules(),i=0;i<g.length;i++)if(f=this._input.match(this.rules[g[i]]),f&&(!u||f[0].length>u[0].length)){if(u=f,d=i,this.options.backtrack_lexer){if(o=this.test_match(f,g[i]),o!==!1)return o;if(this._backtrack){u=!1;continue}else return!1}else if(!this.options.flex)break}return u?(o=this.test_match(u,g[d]),o!==!1?o:!1):this._input===""?this.EOF:this.parseError("Lexical error on line "+(this.yylineno+1)+`. Unrecognized text.
`+this.showPosition(),{text:"",token:null,line:this.yylineno})},"next"),lex:(0,s.eW)(function(){var u=this.next();return u||this.lex()},"lex"),begin:(0,s.eW)(function(u){this.conditionStack.push(u)},"begin"),popState:(0,s.eW)(function(){var u=this.conditionStack.length-1;return u>0?this.conditionStack.pop():this.conditionStack[0]},"popState"),_currentRules:(0,s.eW)(function(){return this.conditionStack.length&&this.conditionStack[this.conditionStack.length-1]?this.conditions[this.conditionStack[this.conditionStack.length-1]].rules:this.conditions.INITIAL.rules},"_currentRules"),topState:(0,s.eW)(function(u){return u=this.conditionStack.length-1-Math.abs(u||0),u>=0?this.conditionStack[u]:"INITIAL"},"topState"),pushState:(0,s.eW)(function(u){this.begin(u)},"pushState"),stateStackSize:(0,s.eW)(function(){return this.conditionStack.length},"stateStackSize"),options:{"case-insensitive":!0},performAction:(0,s.eW)(function(u,f,d,g){var i=g;switch(d){case 0:return this.begin("open_directive"),"open_directive";break;case 1:return this.begin("acc_title"),31;break;case 2:return this.popState(),"acc_title_value";break;case 3:return this.begin("acc_descr"),33;break;case 4:return this.popState(),"acc_descr_value";break;case 5:this.begin("acc_descr_multiline");break;case 6:this.popState();break;case 7:return"acc_descr_multiline_value";case 8:break;case 9:break;case 10:break;case 11:return 10;case 12:break;case 13:break;case 14:this.begin("href");break;case 15:this.popState();break;case 16:return 43;case 17:this.begin("callbackname");break;case 18:this.popState();break;case 19:this.popState(),this.begin("callbackargs");break;case 20:return 41;case 21:this.popState();break;case 22:return 42;case 23:this.begin("click");break;case 24:this.popState();break;case 25:return 40;case 26:return 4;case 27:return 22;case 28:return 23;case 29:return 24;case 30:return 25;case 31:return 26;case 32:return 28;case 33:return 27;case 34:return 29;case 35:return 12;case 36:return 13;case 37:return 14;case 38:return 15;case 39:return 16;case 40:return 17;case 41:return 18;case 42:return 20;case 43:return 21;case 44:return"date";case 45:return 30;case 46:return"accDescription";case 47:return 36;case 48:return 38;case 49:return 39;case 50:return":";case 51:return 6;case 52:return"INVALID"}},"anonymous"),rules:[/^(?:%%\{)/i,/^(?:accTitle\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*:\s*)/i,/^(?:(?!\n||)*[^\n]*)/i,/^(?:accDescr\s*\{\s*)/i,/^(?:[\}])/i,/^(?:[^\}]*)/i,/^(?:%%(?!\{)*[^\n]*)/i,/^(?:[^\}]%%*[^\n]*)/i,/^(?:%%*[^\n]*[\n]*)/i,/^(?:[\n]+)/i,/^(?:\s+)/i,/^(?:%[^\n]*)/i,/^(?:href[\s]+["])/i,/^(?:["])/i,/^(?:[^"]*)/i,/^(?:call[\s]+)/i,/^(?:\([\s]*\))/i,/^(?:\()/i,/^(?:[^(]*)/i,/^(?:\))/i,/^(?:[^)]*)/i,/^(?:click[\s]+)/i,/^(?:[\s\n])/i,/^(?:[^\s\n]*)/i,/^(?:gantt\b)/i,/^(?:dateFormat\s[^#\n;]+)/i,/^(?:inclusiveEndDates\b)/i,/^(?:topAxis\b)/i,/^(?:axisFormat\s[^#\n;]+)/i,/^(?:tickInterval\s[^#\n;]+)/i,/^(?:includes\s[^#\n;]+)/i,/^(?:excludes\s[^#\n;]+)/i,/^(?:todayMarker\s[^\n;]+)/i,/^(?:weekday\s+monday\b)/i,/^(?:weekday\s+tuesday\b)/i,/^(?:weekday\s+wednesday\b)/i,/^(?:weekday\s+thursday\b)/i,/^(?:weekday\s+friday\b)/i,/^(?:weekday\s+saturday\b)/i,/^(?:weekday\s+sunday\b)/i,/^(?:weekend\s+friday\b)/i,/^(?:weekend\s+saturday\b)/i,/^(?:\d\d\d\d-\d\d-\d\d\b)/i,/^(?:title\s[^\n]+)/i,/^(?:accDescription\s[^#\n;]+)/i,/^(?:section\s[^\n]+)/i,/^(?:[^:\n]+)/i,/^(?::[^#\n;]+)/i,/^(?::)/i,/^(?:$)/i,/^(?:.)/i],conditions:{acc_descr_multiline:{rules:[6,7],inclusive:!1},acc_descr:{rules:[4],inclusive:!1},acc_title:{rules:[2],inclusive:!1},callbackargs:{rules:[21,22],inclusive:!1},callbackname:{rules:[18,19,20],inclusive:!1},href:{rules:[15,16],inclusive:!1},click:{rules:[24,25],inclusive:!1},INITIAL:{rules:[0,1,3,5,8,9,10,11,12,13,14,17,23,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52],inclusive:!0}}};return W}();v.lexer=p;function h(){this.yy={}}return(0,s.eW)(h,"Parser"),h.prototype=v,v.Parser=h,new h}();me.parser=me;var tt=me;A.extend(Je),A.extend($e),A.extend(et);var Oe={friday:5,saturday:6},z="",ge="",ve=void 0,pe="",$=[],ee=[],be=new Map,Te=[],ue=[],q="",xe="",Ve=["active","done","crit","milestone","vert"],_e=[],te=!1,we=!1,We="sunday",de="saturday",Ee=0,rt=(0,s.eW)(function(){Te=[],ue=[],q="",_e=[],fe=0,Ce=void 0,ke=void 0,I=[],z="",ge="",xe="",ve=void 0,pe="",$=[],ee=[],te=!1,we=!1,Ee=0,be=new Map,(0,s.ZH)(),We="sunday",de="saturday"},"clear"),st=(0,s.eW)(function(e){ge=e},"setAxisFormat"),it=(0,s.eW)(function(){return ge},"getAxisFormat"),at=(0,s.eW)(function(e){ve=e},"setTickInterval"),nt=(0,s.eW)(function(){return ve},"getTickInterval"),ct=(0,s.eW)(function(e){pe=e},"setTodayMarker"),lt=(0,s.eW)(function(){return pe},"getTodayMarker"),ot=(0,s.eW)(function(e){z=e},"setDateFormat"),ut=(0,s.eW)(function(){te=!0},"enableInclusiveEndDates"),dt=(0,s.eW)(function(){return te},"endDatesAreInclusive"),ft=(0,s.eW)(function(){we=!0},"enableTopAxis"),kt=(0,s.eW)(function(){return we},"topAxisEnabled"),ht=(0,s.eW)(function(e){xe=e},"setDisplayMode"),yt=(0,s.eW)(function(){return xe},"getDisplayMode"),mt=(0,s.eW)(function(){return z},"getDateFormat"),gt=(0,s.eW)(function(e){$=e.toLowerCase().split(/[\s,]+/)},"setIncludes"),vt=(0,s.eW)(function(){return $},"getIncludes"),pt=(0,s.eW)(function(e){ee=e.toLowerCase().split(/[\s,]+/)},"setExcludes"),bt=(0,s.eW)(function(){return ee},"getExcludes"),Tt=(0,s.eW)(function(){return be},"getLinks"),xt=(0,s.eW)(function(e){q=e,Te.push(e)},"addSection"),_t=(0,s.eW)(function(){return Te},"getSections"),wt=(0,s.eW)(function(){let e=Ue();const r=10;let a=0;for(;!e&&a<r;)e=Ue(),a++;return ue=I,ue},"getTasks"),Re=(0,s.eW)(function(e,r,a,c){return c.includes(e.format(r.trim()))?!1:a.includes("weekends")&&(e.isoWeekday()===Oe[de]||e.isoWeekday()===Oe[de]+1)||a.includes(e.format("dddd").toLowerCase())?!0:a.includes(e.format(r.trim()))},"isInvalidDate"),Wt=(0,s.eW)(function(e){We=e},"setWeekday"),Et=(0,s.eW)(function(){return We},"getWeekday"),Dt=(0,s.eW)(function(e){de=e},"setWeekend"),Be=(0,s.eW)(function(e,r,a,c){if(!a.length||e.manualEndTime)return;let n;e.startTime instanceof Date?n=A(e.startTime):n=A(e.startTime,r,!0),n=n.add(1,"d");let y;e.endTime instanceof Date?y=A(e.endTime):y=A(e.endTime,r,!0);const[k,P]=Ct(n,y,r,a,c);e.endTime=k.toDate(),e.renderEndTime=P},"checkTaskDates"),Ct=(0,s.eW)(function(e,r,a,c,n){let y=!1,k=null;for(;e<=r;)y||(k=r.toDate()),y=Re(e,a,c,n),y&&(r=r.add(1,"d")),e=e.add(1,"d");return[r,k]},"fixTaskDates"),De=(0,s.eW)(function(e,r,a){a=a.trim();const n=new RegExp("^after\\s+(?<ids>[\\d\\w- ]+)").exec(a);if(n!==null){let k=null;for(const Y of n.groups.ids.split(" ")){let N=G(Y);N!==void 0&&(!k||N.endTime>k.endTime)&&(k=N)}if(k)return k.endTime;const P=new Date;return P.setHours(0,0,0,0),P}let y=A(a,r.trim(),!0);if(y.isValid())return y.toDate();{s.cM.debug("Invalid date:"+a),s.cM.debug("With date format:"+r.trim());const k=new Date(a);if(k===void 0||isNaN(k.getTime())||k.getFullYear()<-1e4||k.getFullYear()>1e4)throw new Error("Invalid date:"+a);return k}},"getStartDate"),Ye=(0,s.eW)(function(e){const r=/^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(e.trim());return r!==null?[Number.parseFloat(r[1]),r[2]]:[NaN,"ms"]},"parseDuration"),Ne=(0,s.eW)(function(e,r,a,c=!1){a=a.trim();const y=new RegExp("^until\\s+(?<ids>[\\d\\w- ]+)").exec(a);if(y!==null){let C=null;for(const K of y.groups.ids.split(" ")){let V=G(K);V!==void 0&&(!C||V.startTime<C.startTime)&&(C=V)}if(C)return C.startTime;const L=new Date;return L.setHours(0,0,0,0),L}let k=A(a,r.trim(),!0);if(k.isValid())return c&&(k=k.add(1,"d")),k.toDate();let P=A(e);const[Y,N]=Ye(a);if(!Number.isNaN(Y)){const C=P.add(Y,N);C.isValid()&&(P=C)}return P.toDate()},"getEndDate"),fe=0,Q=(0,s.eW)(function(e){return e===void 0?(fe=fe+1,"task"+fe):e},"parseId"),St=(0,s.eW)(function(e,r){let a;r.substr(0,1)===":"?a=r.substr(1,r.length):a=r;const c=a.split(","),n={};Se(c,n,Ve);for(let k=0;k<c.length;k++)c[k]=c[k].trim();let y="";switch(c.length){case 1:n.id=Q(),n.startTime=e.endTime,y=c[0];break;case 2:n.id=Q(),n.startTime=De(void 0,z,c[0]),y=c[1];break;case 3:n.id=Q(c[0]),n.startTime=De(void 0,z,c[1]),y=c[2];break;default:}return y&&(n.endTime=Ne(n.startTime,z,y,te),n.manualEndTime=A(y,"YYYY-MM-DD",!0).isValid(),Be(n,z,ee,$)),n},"compileData"),It=(0,s.eW)(function(e,r){let a;r.substr(0,1)===":"?a=r.substr(1,r.length):a=r;const c=a.split(","),n={};Se(c,n,Ve);for(let y=0;y<c.length;y++)c[y]=c[y].trim();switch(c.length){case 1:n.id=Q(),n.startTime={type:"prevTaskEnd",id:e},n.endTime={data:c[0]};break;case 2:n.id=Q(),n.startTime={type:"getStartDate",startData:c[0]},n.endTime={data:c[1]};break;case 3:n.id=Q(c[0]),n.startTime={type:"getStartDate",startData:c[1]},n.endTime={data:c[2]};break;default:}return n},"parseData"),Ce,ke,I=[],ze={},At=(0,s.eW)(function(e,r){const a={section:q,type:q,processed:!1,manualEndTime:!1,renderEndTime:null,raw:{data:r},task:e,classes:[]},c=It(ke,r);a.raw.startTime=c.startTime,a.raw.endTime=c.endTime,a.id=c.id,a.prevTaskId=ke,a.active=c.active,a.done=c.done,a.crit=c.crit,a.milestone=c.milestone,a.vert=c.vert,a.order=Ee,Ee++;const n=I.push(a);ke=a.id,ze[a.id]=n-1},"addTask"),G=(0,s.eW)(function(e){const r=ze[e];return I[r]},"findTaskById"),Lt=(0,s.eW)(function(e,r){const a={section:q,type:q,description:e,task:e,classes:[]},c=St(Ce,r);a.startTime=c.startTime,a.endTime=c.endTime,a.id=c.id,a.active=c.active,a.done=c.done,a.crit=c.crit,a.milestone=c.milestone,a.vert=c.vert,Ce=a,ue.push(a)},"addTaskOrg"),Ue=(0,s.eW)(function(){const e=(0,s.eW)(function(a){const c=I[a];let n="";switch(I[a].raw.startTime.type){case"prevTaskEnd":{const y=G(c.prevTaskId);c.startTime=y.endTime;break}case"getStartDate":n=De(void 0,z,I[a].raw.startTime.startData),n&&(I[a].startTime=n);break}return I[a].startTime&&(I[a].endTime=Ne(I[a].startTime,z,I[a].raw.endTime.data,te),I[a].endTime&&(I[a].processed=!0,I[a].manualEndTime=A(I[a].raw.endTime.data,"YYYY-MM-DD",!0).isValid(),Be(I[a],z,ee,$))),I[a].processed},"compileTask");let r=!0;for(const[a,c]of I.entries())e(a),r=r&&c.processed;return r},"compileTasks"),Mt=(0,s.eW)(function(e,r){let a=r;(0,s.nV)().securityLevel!=="loose"&&(a=(0,Qe.N)(r)),e.split(",").forEach(function(c){G(c)!==void 0&&(Ke(c,()=>{window.open(a,"_self")}),be.set(c,a))}),je(e,"clickable")},"setLink"),je=(0,s.eW)(function(e,r){e.split(",").forEach(function(a){let c=G(a);c!==void 0&&c.classes.push(r)})},"setClass"),Ft=(0,s.eW)(function(e,r,a){if((0,s.nV)().securityLevel!=="loose"||r===void 0)return;let c=[];if(typeof a=="string"){c=a.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);for(let y=0;y<c.length;y++){let k=c[y].trim();k.startsWith('"')&&k.endsWith('"')&&(k=k.substr(1,k.length-2)),c[y]=k}}c.length===0&&c.push(e),G(e)!==void 0&&Ke(e,()=>{qe.w8.runFunc(r,...c)})},"setClickFun"),Ke=(0,s.eW)(function(e,r){_e.push(function(){const a=document.querySelector(`[id="${e}"]`);a!==null&&a.addEventListener("click",function(){r()})},function(){const a=document.querySelector(`[id="${e}-text"]`);a!==null&&a.addEventListener("click",function(){r()})})},"pushFun"),Pt=(0,s.eW)(function(e,r,a){e.split(",").forEach(function(c){Ft(c,r,a)}),je(e,"clickable")},"setClickEvent"),Ot=(0,s.eW)(function(e){_e.forEach(function(r){r(e)})},"bindFunctions"),Vt={getConfig:(0,s.eW)(()=>(0,s.nV)().gantt,"getConfig"),clear:rt,setDateFormat:ot,getDateFormat:mt,enableInclusiveEndDates:ut,endDatesAreInclusive:dt,enableTopAxis:ft,topAxisEnabled:kt,setAxisFormat:st,getAxisFormat:it,setTickInterval:at,getTickInterval:nt,setTodayMarker:ct,getTodayMarker:lt,setAccTitle:s.GN,getAccTitle:s.eu,setDiagramTitle:s.g2,getDiagramTitle:s.Kr,setDisplayMode:ht,getDisplayMode:yt,setAccDescription:s.U$,getAccDescription:s.Mx,addSection:xt,getSections:_t,getTasks:wt,addTask:At,findTaskById:G,addTaskOrg:Lt,setIncludes:gt,getIncludes:vt,setExcludes:pt,getExcludes:bt,setClickEvent:Pt,setLink:Mt,getLinks:Tt,bindFunctions:Ot,parseDuration:Ye,isInvalidDate:Re,setWeekday:Wt,getWeekday:Et,setWeekend:Dt};function Se(e,r,a){let c=!0;for(;c;)c=!1,a.forEach(function(n){const y="^\\s*"+n+"\\s*$",k=new RegExp(y);e[0].match(k)&&(r[n]=!0,e.shift(1),c=!0)})}(0,s.eW)(Se,"getTaskTags");var Rt=(0,s.eW)(function(){s.cM.debug("Something is calling, setConf, remove the call")},"setConf"),Xe={monday:T.Ox9,tuesday:T.YDX,wednesday:T.EFj,thursday:T.Igq,friday:T.y2j,saturday:T.LqH,sunday:T.Zyz},Bt=(0,s.eW)((e,r)=>{let a=[...e].map(()=>-1/0),c=[...e].sort((y,k)=>y.startTime-k.startTime||y.order-k.order),n=0;for(const y of c)for(let k=0;k<a.length;k++)if(y.startTime>=a[k]){a[k]=y.endTime,y.order=k+r,k>n&&(n=k);break}return n},"getMaxIntersections"),j,Yt=(0,s.eW)(function(e,r,a,c){const n=(0,s.nV)().gantt,y=(0,s.nV)().securityLevel;let k;y==="sandbox"&&(k=(0,T.Ys)("#i"+r));const P=y==="sandbox"?(0,T.Ys)(k.nodes()[0].contentDocument.body):(0,T.Ys)("body"),Y=y==="sandbox"?k.nodes()[0].contentDocument:document,N=Y.getElementById(r);j=N.parentElement.offsetWidth,j===void 0&&(j=1200),n.useWidth!==void 0&&(j=n.useWidth);const C=c.db.getTasks();let L=[];for(const m of C)L.push(m.type);L=oe(L);const K={};let V=2*n.topPadding;if(c.db.getDisplayMode()==="compact"||n.displayMode==="compact"){const m={};for(const v of C)m[v.section]===void 0?m[v.section]=[v]:m[v.section].push(v);let b=0;for(const v of Object.keys(m)){const p=Bt(m[v],b)+1;b+=p,V+=p*(n.barHeight+n.barGap),K[v]=p}}else{V+=C.length*(n.barHeight+n.barGap);for(const m of L)K[m]=C.filter(b=>b.type===m).length}N.setAttribute("viewBox","0 0 "+j+" "+V);const R=P.select(`[id="${r}"]`),w=(0,T.Xf)().domain([(0,T.VV$)(C,function(m){return m.startTime}),(0,T.Fp7)(C,function(m){return m.endTime})]).rangeRound([0,j-n.leftPadding-n.rightPadding]);function re(m,b){const v=m.startTime,p=b.startTime;let h=0;return v>p?h=1:v<p&&(h=-1),h}(0,s.eW)(re,"taskCompare"),C.sort(re),se(C,j,V),(0,s.v2)(R,V,j,n.useMaxWidth),R.append("text").text(c.db.getDiagramTitle()).attr("x",j/2).attr("y",n.titleTopMargin).attr("class","titleText");function se(m,b,v){const p=n.barHeight,h=p+n.barGap,W=n.topPadding,o=n.leftPadding,u=(0,T.BYU)().domain([0,L.length]).range(["#00B9FA","#F95002"]).interpolate(T.JHv);ae(h,W,o,b,v,m,c.db.getExcludes(),c.db.getIncludes()),ne(o,W,b,v),ie(m,h,W,o,p,u,b,v),ce(h,W,o,p,u),le(o,W,b,v)}(0,s.eW)(se,"makeGantt");function ie(m,b,v,p,h,W,o){m.sort((l,t)=>l.vert===t.vert?0:l.vert?1:-1);const f=[...new Set(m.map(l=>l.order))].map(l=>m.find(t=>t.order===l));R.append("g").selectAll("rect").data(f).enter().append("rect").attr("x",0).attr("y",function(l,t){return t=l.order,t*b+v-2}).attr("width",function(){return o-n.rightPadding/2}).attr("height",b).attr("class",function(l){for(const[t,E]of L.entries())if(l.type===E)return"section section"+t%n.numberSectionStyles;return"section section0"}).enter();const d=R.append("g").selectAll("rect").data(m).enter(),g=c.db.getLinks();if(d.append("rect").attr("id",function(l){return l.id}).attr("rx",3).attr("ry",3).attr("x",function(l){return l.milestone?w(l.startTime)+p+.5*(w(l.endTime)-w(l.startTime))-.5*h:w(l.startTime)+p}).attr("y",function(l,t){return t=l.order,l.vert?n.gridLineStartPadding:t*b+v}).attr("width",function(l){return l.milestone?h:l.vert?.08*h:w(l.renderEndTime||l.endTime)-w(l.startTime)}).attr("height",function(l){return l.vert?C.length*(n.barHeight+n.barGap)+n.barHeight*2:h}).attr("transform-origin",function(l,t){return t=l.order,(w(l.startTime)+p+.5*(w(l.endTime)-w(l.startTime))).toString()+"px "+(t*b+v+.5*h).toString()+"px"}).attr("class",function(l){const t="task";let E="";l.classes.length>0&&(E=l.classes.join(" "));let _=0;for(const[M,D]of L.entries())l.type===D&&(_=M%n.numberSectionStyles);let x="";return l.active?l.crit?x+=" activeCrit":x=" active":l.done?l.crit?x=" doneCrit":x=" done":l.crit&&(x+=" crit"),x.length===0&&(x=" task"),l.milestone&&(x=" milestone "+x),l.vert&&(x=" vert "+x),x+=_,x+=" "+E,t+x}),d.append("text").attr("id",function(l){return l.id+"-text"}).text(function(l){return l.task}).attr("font-size",n.fontSize).attr("x",function(l){let t=w(l.startTime),E=w(l.renderEndTime||l.endTime);if(l.milestone&&(t+=.5*(w(l.endTime)-w(l.startTime))-.5*h,E=t+h),l.vert)return w(l.startTime)+p;const _=this.getBBox().width;return _>E-t?E+_+1.5*n.leftPadding>o?t+p-5:E+p+5:(E-t)/2+t+p}).attr("y",function(l,t){return l.vert?n.gridLineStartPadding+C.length*(n.barHeight+n.barGap)+60:(t=l.order,t*b+n.barHeight/2+(n.fontSize/2-2)+v)}).attr("text-height",h).attr("class",function(l){const t=w(l.startTime);let E=w(l.endTime);l.milestone&&(E=t+h);const _=this.getBBox().width;let x="";l.classes.length>0&&(x=l.classes.join(" "));let M=0;for(const[Ie,S]of L.entries())l.type===S&&(M=Ie%n.numberSectionStyles);let D="";return l.active&&(l.crit?D="activeCritText"+M:D="activeText"+M),l.done?l.crit?D=D+" doneCritText"+M:D=D+" doneText"+M:l.crit&&(D=D+" critText"+M),l.milestone&&(D+=" milestoneText"),l.vert&&(D+=" vertText"),_>E-t?E+_+1.5*n.leftPadding>o?x+" taskTextOutsideLeft taskTextOutside"+M+" "+D:x+" taskTextOutsideRight taskTextOutside"+M+" "+D+" width-"+_:x+" taskText taskText"+M+" "+D+" width-"+_}),(0,s.nV)().securityLevel==="sandbox"){let l;l=(0,T.Ys)("#i"+r);const t=l.nodes()[0].contentDocument;d.filter(function(E){return g.has(E.id)}).each(function(E){var _=t.querySelector("#"+E.id),x=t.querySelector("#"+E.id+"-text");const M=_.parentNode;var D=t.createElement("a");D.setAttribute("xlink:href",g.get(E.id)),D.setAttribute("target","_top"),M.appendChild(D),D.appendChild(_),D.appendChild(x)})}}(0,s.eW)(ie,"drawRects");function ae(m,b,v,p,h,W,o,u){if(o.length===0&&u.length===0)return;let f,d;for(const{startTime:_,endTime:x}of W)(f===void 0||_<f)&&(f=_),(d===void 0||x>d)&&(d=x);if(!f||!d)return;if(A(d).diff(A(f),"year")>5){s.cM.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");return}const g=c.db.getDateFormat(),i=[];let l=null,t=A(f);for(;t.valueOf()<=d;)c.db.isInvalidDate(t,g,o,u)?l?l.end=t:l={start:t,end:t}:l&&(i.push(l),l=null),t=t.add(1,"d");R.append("g").selectAll("rect").data(i).enter().append("rect").attr("id",function(_){return"exclude-"+_.start.format("YYYY-MM-DD")}).attr("x",function(_){return w(_.start)+v}).attr("y",n.gridLineStartPadding).attr("width",function(_){const x=_.end.add(1,"day");return w(x)-w(_.start)}).attr("height",h-b-n.gridLineStartPadding).attr("transform-origin",function(_,x){return(w(_.start)+v+.5*(w(_.end)-w(_.start))).toString()+"px "+(x*m+.5*h).toString()+"px"}).attr("class","exclude-range")}(0,s.eW)(ae,"drawExcludeDays");function ne(m,b,v,p){let h=(0,T.LLu)(w).tickSize(-p+b+n.gridLineStartPadding).tickFormat((0,T.i$Z)(c.db.getAxisFormat()||n.axisFormat||"%Y-%m-%d"));const o=/^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(c.db.getTickInterval()||n.tickInterval);if(o!==null){const u=o[1],f=o[2],d=c.db.getWeekday()||n.weekday;switch(f){case"millisecond":h.ticks(T.U8T.every(u));break;case"second":h.ticks(T.S1K.every(u));break;case"minute":h.ticks(T.Z_i.every(u));break;case"hour":h.ticks(T.WQD.every(u));break;case"day":h.ticks(T.rr1.every(u));break;case"week":h.ticks(Xe[d].every(u));break;case"month":h.ticks(T.F0B.every(u));break}}if(R.append("g").attr("class","grid").attr("transform","translate("+m+", "+(p-50)+")").call(h).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10).attr("dy","1em"),c.db.topAxisEnabled()||n.topAxis){let u=(0,T.F5q)(w).tickSize(-p+b+n.gridLineStartPadding).tickFormat((0,T.i$Z)(c.db.getAxisFormat()||n.axisFormat||"%Y-%m-%d"));if(o!==null){const f=o[1],d=o[2],g=c.db.getWeekday()||n.weekday;switch(d){case"millisecond":u.ticks(T.U8T.every(f));break;case"second":u.ticks(T.S1K.every(f));break;case"minute":u.ticks(T.Z_i.every(f));break;case"hour":u.ticks(T.WQD.every(f));break;case"day":u.ticks(T.rr1.every(f));break;case"week":u.ticks(Xe[g].every(f));break;case"month":u.ticks(T.F0B.every(f));break}}R.append("g").attr("class","grid").attr("transform","translate("+m+", "+b+")").call(u).selectAll("text").style("text-anchor","middle").attr("fill","#000").attr("stroke","none").attr("font-size",10)}}(0,s.eW)(ne,"makeGrid");function ce(m,b){let v=0;const p=Object.keys(K).map(h=>[h,K[h]]);R.append("g").selectAll("text").data(p).enter().append(function(h){const W=h[0].split(s.SY.lineBreakRegex),o=-(W.length-1)/2,u=Y.createElementNS("http://www.w3.org/2000/svg","text");u.setAttribute("dy",o+"em");for(const[f,d]of W.entries()){const g=Y.createElementNS("http://www.w3.org/2000/svg","tspan");g.setAttribute("alignment-baseline","central"),g.setAttribute("x","10"),f>0&&g.setAttribute("dy","1em"),g.textContent=d,u.appendChild(g)}return u}).attr("x",10).attr("y",function(h,W){if(W>0)for(let o=0;o<W;o++)return v+=p[W-1][1],h[1]*m/2+v*m+b;else return h[1]*m/2+b}).attr("font-size",n.sectionFontSize).attr("class",function(h){for(const[W,o]of L.entries())if(h[0]===o)return"sectionTitle sectionTitle"+W%n.numberSectionStyles;return"sectionTitle"})}(0,s.eW)(ce,"vertLabels");function le(m,b,v,p){const h=c.db.getTodayMarker();if(h==="off")return;const W=R.append("g").attr("class","today"),o=new Date,u=W.append("line");u.attr("x1",w(o)+m).attr("x2",w(o)+m).attr("y1",n.titleTopMargin).attr("y2",p-n.titleTopMargin).attr("class","today"),h!==""&&u.attr("style",h.replace(/,/g,";"))}(0,s.eW)(le,"drawToday");function oe(m){const b={},v=[];for(let p=0,h=m.length;p<h;++p)Object.prototype.hasOwnProperty.call(b,m[p])||(b[m[p]]=!0,v.push(m[p]));return v}(0,s.eW)(oe,"checkUnique")},"draw"),Nt={setConf:Rt,draw:Yt},zt=(0,s.eW)(e=>`
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
`,"getStyles"),Ut=zt,jt={parser:tt,db:Vt,renderer:Nt,styles:Ut}}}]);
