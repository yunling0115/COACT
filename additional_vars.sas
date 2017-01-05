/*----------------------------------------------------------------------------------------*/
/* 
input:
(1) permno_fdate.txt
varaibles:
(1) computstat (yearly)
(2) lagged compustat (yearly)
(3) market equity (yearly, end-of-year)
(4) number of analysts (this quarter)
(5) past 12 month return (12 month - to this month)
(6) amihud (yearly)
(7) institutional holdings (this quarter)
(8) abnormal return and abnormal volume
*/

options nodate nocenter nonumber ps=max ls=max symbolgen macrogen mlogic mprint;
options nosource;
options source;

proc upload data=permno_fdate_collude out=permno_fdate_collude; run;

/* distinct permno, fdate, date and drop those without fdate and date */
proc sql;
	create table permno_fdate_collude
	as select distinct permno, fdate, date
	from permno_fdate_collude where fdate~=.;
quit;
run;
proc sort data=permno_fdate_collude; by permno fdate;

/* Compustat data: (using crsp.ccmxpf_linktable, comp.funda, comp.aco_pnfnda, comp.company) */

%let keys= gvkey fyr fyear datadate indfmt datafmt popsrc consol;
%let vars= cusip at lt fopt capx sppe xrd dvpsx_c ch che dlc dltt sale seq ceq 
	pstk pstkrv pstkl mib txditc ni dvc dvt ib txdb ebit ebitda tic re act lct;	
%let lvars = at sale;
proc sql;
	create table link
	as select distinct a.*, b.gvkey, b.linkdt, b.linkenddt
	from permno_fdate_collude as a left join crsp.ccmxpf_linktable as b
	on a.permno=b.lpermno and b.linktype in ("LU", "LC", "LD", "LF", "LN", "LO", "LS", "LX")
	and (a.date>=b.linkdt or b.linkdt=.B)
	and (a.date<=b.linkenddt or b.linkenddt=.E);
quit;

proc sql;
	create table compustat
	as select distinct *
	from link as a left join comp.funda (keep = &keys &vars) as b
	on a.gvkey=b.gvkey and 
	/* calendar_year=fyear(6<=fyr<=12) or fyear+1(1<=fyr<=5) */
    ((year(a.date)=b.fyear and 6<=b.fyr<=12) or (year(a.date)=b.fyear+1 and 1<=b.fyr<=5))
	and b.indfmt='INDL' and b.datafmt='STD' and b.popsrc='D' and b.consol='C'
	and (a.linkdt<=b.datadate or a.linkdt=.B)
	and (b.datadate<=a.linkenddt or a.linkenddt=.E);

	/* prba */
	create table compustat
	as select distinct *
	from compustat as a left join 
	comp.aco_pnfnda (keep=gvkey indfmt consol datafmt popsrc datadate prba) as b
	on a.gvkey=b.gvkey and a.indfmt=b.indfmt and a.consol=b.consol and a.datafmt=b.datafmt 
   	and a.popsrc=b.popsrc and a.datadate=b.datadate;

	/* sic and naics */
	create table compustat
	as select distinct *
	from compustat as a left join
	comp.company (keep=gvkey sic naics) as b
	on a.gvkey=b.gvkey;
quit;

/* lagged Compustat */

proc sql;
	create table lcompustat
	as select distinct *
	from link as a left join comp.funda (keep = &keys &lvars) as b
	on a.gvkey=b.gvkey and 
	/* calendar_year=fyear(6<=fyr<=12) or fyear+1(1<=fyr<=5) */
    ((year(a.date)-1=b.fyear and 6<=b.fyr<=12) or (year(a.date)-1=b.fyear+1 and 1<=b.fyr<=5))
	and b.indfmt='INDL' and b.datafmt='STD' and b.popsrc='D' and b.consol='C'
	and (a.linkdt<=b.datadate or a.linkdt=.B)
	and (b.datadate<=a.linkenddt or a.linkenddt=.E);
quit;
%macro rename(oldvarlist, prefix);
  %let k=1;
  %let old = %scan(&oldvarlist, &k);
     %do %while("&old" NE "");
      rename &old = &prefix.&old.;
	  %let k = %eval(&k + 1);
      %let old = %scan(&oldvarlist, &k);
  %end;
%mend;
data lcompustat;
	set lcompustat;
	keep permno fdate date &lvars;
	%rename(&lvars , L);
run;

/* market equity (crsp.msf) */

proc sql;
	create table me
	as select distinct a.*, b.shrout as shrout, abs(b.prc) as prc, abs(b.prc)*b.shrout as me
	from permno_fdate_collude as a left join crsp.msf (where=(month(date)=12)) as b
	on a.permno=b.permno and year(a.date)=year(b.date) and (abs(b.prc)*b.shrout)>0;
quit;
proc sort data=me; by permno date; run;

/* ibes: # of analysts (using home.iclink and ibes.statsum_epsus)*/

proc sql;
	create table temp
	as select distinct a.*, b.ticker, b.cname from 
	permno_fdate_collude as a left join home.iclink as b
	on a.permno=b.permno;

	create table analyst 
	as select distinct a.permno, a.fdate, a.date, 
	avg(b.numest) as analyst from
	temp a left join ibes.statsum_epsus as b
	on a.ticker=b.ticker and intck('qtr',a.fdate,b.actdats_act)=0
	group by a.permno, a.date;
quit;

/* stkret12: past 12 month return */

proc sql;
	create table stkret12
	as select distinct a.*, exp(sum(log(1+b.ret)))-1 as stkret from
	permno_fdate_collude as a left join crsp.msf as b
	on a.permno=b.permno and b.date<a.date and intnx('month',b.date,13)>=a.date
	group by a.permno, a.date;
quit;

/* Amihud (2002) illiquidity: yearly average (using daily data) of 1000*sqrt(|return|/(Dollar Trading Volume)) */

data permno_fdate_collude;
	set permno_fdate_collude;
	year = year(fdate);
run;
proc sql;
	create table permno_year
	as select distinct permno, year
	from permno_fdate_collude;
run;
proc sql;
	create table amihud_year
	as select distinct a.*, avg(1000*sqrt(abs(b.ret)/b.vol)) as amihud from
	permno_year as a left join crsp.dsf as b 
	on a.permno=b.permno and a.year=year(b.date)
	group by a.permno, a.year;
quit;
proc sql;
	create table amihud
	as select distinct a.*, b.amihud, b.year from
	permno_fdate_collude as a left join amihud_year as b
	on a.permno=b.permno and year(a.date)=b.year
	group by a.permno, a.year;
quit;

/* inst: institutional holdings (using tfn.s34) */

data tfn;
	set tfn.s34 (keep = rdate cusip shrout1 shrout2 shares);
	where 1992<=year(rdate)<=2014;
run;
proc sql;
	create table inst
	as select distinct a.*, sum(shares) as inst, avg(shrout1) as shrout1, avg(shrout2) as shrout2 from
	compustat (keep=permno cusip fdate date) as a left join tfn as b
	on substr(a.cusip,1,8)=b.cusip and intck('qtr',a.fdate,b.rdate)=0
	group by a.permno, a.date;
quit;

data inst;
	set inst;
	total_shares_out= shrout1*1000000;
	if shrout2 > 0 then total_shares_out= shrout2*1000;
	held_pct=inst/total_shares_out;
	drop shrout1 shrout2;
run;


/* abret: abnormal returns and abnormal turnover (using crsp.dsf, ff.factors_daily) */
/* abret - buy and hold return during (-20,+20)-day window around fdate in excess of 
	the buy and hold return on the value-weighted market */
/* abvol - share trading turnover during (-20,+20)-day window compared to the average
	turnover rate during the preceding (-100,-40)-day window */

%let evt_beg=-20;
%let evt_end=20;
%let eva_beg=-100;
%let eva_end=-40;
proc sql;
	create table ret
	as select distinct a.*, exp(sum(log(1+b.ret)))-1 as ret, sum(b.vol)/avg(b.shrout) as turnover
	from permno_fdate_collude as a left join crsp.dsf as b
	on a.permno=b.permno and intck('day',a.date,b.date)>=&evt_beg and intck('day',a.date,b.date)<=&evt_end
	group by a.permno, a.fdate;
quit;
proc sql;
	create table mktrf
	as select distinct a.*, exp(sum(log(1+b.mktrf)))-1 as mktrf
	from permno_fdate_collude as a left join ff.factors_daily as b
	on intck('day',a.date,b.date)>=&evt_beg and intck('day',a.date,b.date)<=&evt_end
	group by a.permno, a.fdate;
quit;
proc sql;
	create table eva
	as select distinct a.*, sum(b.vol)/avg(b.shrout) as evaturnover
	from permno_fdate_collude as a left join crsp.dsf as b
	on a.permno=b.permno and intck('day',a.date,b.date)>=&eva_beg and intck('day',a.date,b.date)<=&eva_end
	group by a.permno, a.fdate;
quit;
data abret;
	merge ret mktrf eva;
	by permno fdate;
	abret=ret-mktrf;
	abturnover=turnover-evaturnover;
	drop mktrf evaturnover;
run;

/* g-index: irrc */

/* merging */
data sas;
	merge compustat lcompustat me amihud stkret12 analyst inst abret;
	by permno date;
run;

/* download */
proc download data=sas out=sas; run;




