/*----------------------------------------------------------------------------------------*/
/* 13D - Benchmark (after getting size_bm [yearly]) */
/* 
input:
(1) size_bm_port
varaibles:
(1) computstat (yearly)
(2) lagged compustat (yearly)
(3) market equity (yearly, end-of-year)
(4) number of analysts (this quarter -> yearly, 4 vars)
(5) past 12 month return (12 month - to this month -> yearly, 12 vars)
(6) amihud (yearly)
(7) institutional holdings (this quarter -> yearly, 4 vars)
*/

options nodate nocenter nonumber ps=max ls=max symbolgen macrogen mlogic mprint;
options nosource;
options source;

/* Compustat data: (using crsp.ccmxpf_linktable, comp.funda, comp.aco_pnfnda, comp.company) */
%let keys= gvkey fyr fyear datadate indfmt datafmt popsrc consol;
%let vars= cusip at lt fopt capx sppe xrd dvpsx_c ch che dlc dltt sale seq ceq 
	pstk pstkrv pstkl mib txditc ni dvc dvt ib txdb ebit ebitda tic re act lct;	
%let lvars = at sale;
proc sql;
	create table link
	as select distinct a.*, b.gvkey, b.linkdt, b.linkenddt
	from &filename as a left join crsp.ccmxpf_linktable as b
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
	keep permno gvkey date &lvars;
	%rename(&lvars , L);
run;

/* market equity (crsp.msf) */

proc sql;
	create table me
	as select distinct a.*, b.shrout as shrout, abs(b.prc) as prc, abs(b.prc)*b.shrout as me
	from &filename as a left join crsp.msf (where=(month(date)=12)) as b
	on a.permno=b.permno and year(a.date)=year(b.date) and (abs(b.prc)*b.shrout)>0;
quit;
proc sort data=me; by permno date; run;

/* ibes: # of analysts (using home.iclink and ibes.statsum_epsus) - Quarters 1-4 */

proc sql;
	create table temp
	as select distinct a.*, b.ticker, b.cname from 
	&filename as a left join home.iclink as b
	on a.permno=b.permno;
quit;
data statsum_epsus (keep= ticker numest year quarter);
	set ibes.statsum_epsus (keep= ticker numest actdats_act);
	year = year(actdats_act);
	quarter = qtr(actdats_act);
run;
proc sql;
	create table statsum_epsus
	as select distinct ticker, year, quarter, avg(numest) as numest
	from statsum_epsus group by ticker, year, quarter;
run;
proc transpose data = statsum_epsus out = statsum_epsus_wide (drop=_NAME_) prefix=numest;
	by ticker year;
	id quarter;
	var numest;
run;
proc sql;
	create table analyst 
	as select distinct * from
	temp as a left join statsum_epsus_wide as b
	on a.ticker=b.ticker and year(a.date)=b.year
	order by permno, date;
quit;

/* stkret12: past 12 month return - Months 1-12 */

data msf;
	set crsp.msf (keep=permno date ret);
	where 2013<=year(date)<=2014;
run;
proc sql;
	create table ret12
	as select distinct a.permno, month(a.date) as month, year(a.date) as year, exp(sum(log(1+b.ret)))-1 as stkret from
	msf as a left join crsp.msf (keep=permno date ret) as b
	on a.permno=b.permno and b.date<a.date and intnx('month',b.date,13)>=a.date
	group by a.permno, year, month;
run;
proc sort data=ret12; by permno year month; run;
proc transpose data = ret12 out = ret12_wide (drop=_NAME_) prefix=stkret;
	by permno year;
	id month;
	var stkret;
run;
proc sql;
	create table stkret12
	as select distinct * from
	&filename as a left join ret12_wide as b
	on a.permno=b.permno and year(a.date)=b.year
	order by permno, date;
quit;

/* Amihud (2002) illiquidity: yearly average (using daily data) of 1000*sqrt(|return|/(Dollar Trading Volume)) */

data dsf;
	set crsp.dsf (keep=permno date ret vol);
	where 2013<=year(date)<=2014;
	year = year(date);
run;
proc sql;
	create table amihud_year
	as select distinct permno, year, avg(1000*sqrt(abs(ret)/vol)) as amihud from
	dsf group by permno, year;
run;
proc sql;
	create table amihud
	as select distinct a.*, b.amihud from
	&filename as a left join amihud_year as b
	on a.permno=b.permno and year(a.date)=b.year
	order by a.permno, a.date;
run;

/* inst: institutional holdings (using tfn.s34) - Quarters 1-4 */
data tfn;
	set tfn.s34 (keep = rdate cusip shrout1 shrout2 shares);
	year = year(rdate);
	quarter = qtr(rdate);
	where 2013<=year(rdate)<=2014;
run;
proc sql;
	create table inst
	as select distinct cusip, year, quarter, sum(shares) as inst, avg(shrout1) as shrout1, avg(shrout2) as shrout2
	from tfn group by cusip, year, quarter;
run;
data inst;
	set inst;
	total_shares_out= shrout1*1000000;
	if shrout2 > 0 then total_shares_out= shrout2*1000;
	held_pct=inst/total_shares_out;
	drop shrout1 shrout2;
run;
proc transpose data=inst out=inst1_wide (drop=_NAME_) prefix=inst;
	by cusip year;
	id quarter;
	var inst;
run;
proc transpose data=inst out=inst2_wide (drop=_NAME_) prefix=held_pct;
	by cusip year;
	id quarter;
	var inst;
run;
proc transpose data=inst out=inst3_wide (drop=_NAME_) prefix=total_shares_out;
	by cusip year;
	id quarter;
	var inst;
run;
data inst;
	merge inst1_wide inst2_wide inst3_wide;
	by cusip year;
run;
proc sql;
	create table inst
	as select distinct * from compustat (keep=permno cusip date) as a left join inst as b
	on substr(a.cusip,1,8)=b.cusip and year(a.date) = b.year
	order by a.permno, a.date;
run;

/* g-index: irrc */

/* merging */

proc sort data=compustat; by permno date; run;
proc sort data=lcompustat; by permno date; run;
proc sort data=me; by permno date; run;
proc sort data=amihud; by permno date; run;
proc sort data=stkret12; by permno date; run;
proc sort data=analyst; by permno date; run;
proc sort data=inst; by permno date; run;
data sas;
	merge compustat lcompustat me amihud stkret12 analyst inst;
	by permno date;
run;

/* download */
rsubmit;
proc download data=sas out=sas; run;
