


SELECT count(id) as firmcount, SUM(array_length(bypage, 1)) as totalpages, SUM(array_length(externalurls , 1)) as foundexternal, SUM(array_length(domainurls , 1)) as foundinternal FROM targetlist WHERE bypage IS NOT null AND processingstatus = 'SCRAPE1'; 



select processingstatus , count(id) from targetlist t group by processingstatus ;

select * from targetlist t where processingstatus ='SCRAPE0' limit 5;

select * from targetlist t where processingstatus ='NEW' and urls is not null limit 5;

select count(*) from targetlist t ;

select * from targetlist t where uniquebuskey ='300151' order by total_gross_assets_of_private_funds ;

select * from targetlist t order by createdon desc;

select count(*) from targetlist t  ;

UPDATE targetlist SET processingstatus = 'NEW' ;



update targetlist set processingstatus = 'NEW' where processingstatus = 'SCRAPEFAILED';

UPDATE targetlist 
SET urls = COALESCE(urls, ARRAY[]::text[]) || ARRAY[alltext] 
where alltext IS NOT NULL;


select id, primary_business_name, uniquebuskey, processingstatus, website_address, urls, domainurls, externalurls, bypage, notes 
from targetlist t
where processingstatus ='SCRAPE1';


select id, primary_business_name, uniquebuskey, processingstatus, website_address, urls, domainurls, externalurls, bypage, notes 
from targetlist t
where uniquebuskey ='107750';


select id, primary_business_name, uniquebuskey, processingstatus, website_address, urls, domainurls, externalurls, bypage, notes 
from targetlist t
where processingstatus = 'SCRAPE0'
and domainurls is not null
limit 10;



SELECT id, uniquebuskey, processingstatus, primary_business_name, urls
FROM public.targetlist 
WHERE processingstatus = 'SCRAPE1'


