
SELECT * FROM public.targetlist t where primary_business_name like '%NUTS%';

SELECT * FROM public.targetlist t where uniquebuskey ='329065';

UPDATE public.targetlist
SET urls = array_append(urls, website_address::text)
WHERE uniquebuskey ='329065';


select   domainurls, externalurls, bypage, structdata, urls, website_address, uniquebuskey, primary_business_name , notes, processingstatus 
from targetlist t
where uniquebuskey  = '171606'
; 


UPDATE public.targetlist SET processingstatus = '{}', externalurls = '{}', domainurls = '{}', urls = '{}', notes = ARRAY[]::jsonb[], bypage = ARRAY[]::jsonb[], structdata = ARRAY[]::jsonb[]
where uniquebuskey  = '329065'
; 

REINDEX TABLE public.targetlist;


UPDATE public.targetlist SET processingstatus = '{}', externalurls = '{}', domainurls = '{}', urls = '{}', notes = ARRAY[]::jsonb[], bypage = ARRAY[]::jsonb[], structdata = ARRAY[]::jsonb[]  WHERE "uniquebuskey" = '173158';