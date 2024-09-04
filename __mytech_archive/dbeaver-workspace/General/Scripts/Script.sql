select * from targetlist t;
commit;
SELECT table_name, column_name, data_type, udt_name, character_maximum_length

SELECT *
                        FROM information_schema.columns c 
                        WHERE c.table_name NOT LIKE 'pg%'
                        AND c.table_schema <> 'information_schema';


                       select 'New' "Status", count("id") from targetlist t where processingstatus <>'NEW' union 
                       select '';
                      
                                             select count("id") from targetlist t where processingstatus is null;
                                            update targetlist set processingstatus = 'NEW' where processingstatus is null;                     

                                           
SELECT id, uniquebuskey, processingstatus, primary_business_name, urls
FROM public.targetlist 
WHERE processingstatus = 'SCRAPE1'



select processingstatus , count(id) from targetlist t group by processingstatus ;



update public.targetlist set processingstatus = 'NEW';

SHOW standard_conforming_strings;

select * from textlibrary t where rowcontext ='test_context';




update targetlist set urls = urls || email_address ;



delete from textlibrary t where t.rowcontext ='test_context';

update textlibrary set uniquebuskey =id ;

alter table textlibrary add parentname varchar(250) null;


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

update "PrivateAsset" set "RecordContext" = 'PRIVATEASSET' where "SymTicker" is null or "SymTicker" ='';


CREATE TABLE IF NOT EXISTS targetlist (
                id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                rowcontext varchar(100) NULL,
                uniquebuskey varchar(250) NULL,
                processingstatus varchar(50) NULL,
                Organization_CRD varchar(100) NULL,
                SEC varchar(100) NULL,
                Primary_Business_Name varchar(100) NULL,
                Legal_Name varchar(100) NULL,
                Main_Office_Location jsonb NULL,
                Main_Office_Telephone_Number varchar(50) NULL,
                SEC_Executive jsonb NULL,
                SEC_Status_Effective_Date varchar(100) NULL,
                Website_Address varchar(500) NULL,
                Entity_Type varchar(200) NULL,
                Governing_Country varchar(100) NULL,
                Total_Gross_Assets_of_Private_Funds DECIMAL,
                Next_Pipeline_Stage varchar(100) NULL,
                Notes jsonb[] NULL,
                title varchar(500) NULL,
                description varchar(500) NULL,
                summary text NULL,
                names text[] NULL,
                emails text[] NULL,
                contacts text[] NULL,
                clients text[] NULL,
                partners text[] NULL,
                companies text[] NULL,
                experience text[] NULL,
                entities text[] NULL,
                needs text[] NULL,
                economics text[] NULL,
                competitors text[] NULL,
                decisionprocesses text[] NULL,
                timelines text[] NULL,
                sasactivity jsonb[] NULL,
                sasstage jsonb[] NULL,
                urls text [] NULL,
                domainurls text [] NULL,
                externalurls text [] NULL,
                scrapedurls text [] NULL,
                urllevellookup jsonb[] NULL,
                authors text[] NULL,
                publishdate date null,
                sourcefilename varchar(100) null,
                contenttype varchar(100) null,
                structdata jsonb[] NULL,
                bypage jsonb[] NULL,
                allpages jsonb[] NULL,
                summaryparts jsonb[] NULL,
                alltext text NULL,
                topics text[] NULL,
                speakers text[] NULL,
                binarydoc bytea NULL,
                documentids int[] NULL,
                imageids int[] NULL,
                sentiment varchar(100) NULL,
                createdon timestamp DEFAULT CURRENT_TIMESTAMP NULL,
                archivedon timestamp NULL,
                iscurrent bool DEFAULT true NULL,
                createdby varchar(50) NULL,
                archivedby varchar(50) NULL,
                loadsource varchar(10) null);

CREATE UNIQUE INDEX idx_rowcontext_targetcurrent ON targetlist USING btree (rowcontext, uniquebuskey) WHERE (iscurrent = true);

CREATE INDEX idx_non_uniquetar_rowcontext ON targetlist (rowcontext);
CREATE INDEX idx_non_uniquetar_uniquebuskey ON targetlist (uniquebuskey);
commit;



SELECT * 
FROM "PrivateAsset" pa 
WHERE pa."AccountId" IN (SELECT a."Id"  FROM "Account" a);


SELECT * FROM information_schema.columns c where c.table_name not like 'pg\_%' and c.table_name not like  '\_pg%' and c.table_schema <> 'information_schema' order by c.data_type;

SELECT distinct(c.udt_name) from information_schema.columns c where c.table_name not like 'pg%' and c.table_schema <> 'information_schema';;


select * from targetlist;

select * from targetlist t where emailisvalid ='N	';

select * from targetlist t where emailisvalid ='Y';

select count(*) from targetlist;


update targetlist t  set emailisvalid = 'Y';

UPDATE targetlist SET emailisvalid = 'N' where website_address is null;

UPDATE targetlist SET alltext = Null ;



select * from targetlist t where emailisvalid is null


UPDATE targetlist SET website_address = LOWER(website_address);


UPDATE targetlist SET urls = COALESCE(urls, ARRAY[]::text[]) || ARRAY[alltext::text] where urls is null and alltext is not null;


SELECT SUBSTRING(email_address FROM POSITION('@' IN email_address) + 1) AS email_domain
FROM targetlist;



UPDATE targetlist
SET alltext = lower(CONCAT('https://www.', SUBSTRING(email_address FROM POSITION('@' IN email_address) + 1))), emailisvalid = 'Y'
WHERE emailisvalid is null
and email_address not ILIKE ANY (ARRAY[
    '%gmail%',
    '%yahoo%',
    '%google%',
    '%hotmail%',
    '%aol.com%',
    '%outlook%',
    '%icloud%',
    '%tumbler%',
    '%protonmail%',
    '%linkedin%',
    '%facebook%',
    '%twitter%',
    '%youtube%',
    '%instagram%',
    '%vimeo%',
    '%glassdoor%',
    '%tiktok%',
    '%podbean%',
    '%apple%',
    '%soundcloud%',
    '%spotify%',
    '%reddit%',
    '%me.com%',
    '%mac.com%',
    '%live.com%',
    '%msn.com%',
    '%att.com%',
    '%sbcglobal%',
    '%twitter%',
    '%bellsouth%',
    '%verizon%',
    '%cox.net%',
    '%charter.net%',
    '%earthlink%',
    '%juno.com%',
    '%optonline%',
    '%netzero%',
    '%frontiernet%',
    '%windstream%',
    '%suddenlink%',
    '%cableone%',
    '%centurylink%'
]);



UPDATE targetlist
SET emailisvalid = 'N'
WHERE website_address ILIKE ANY (ARRAY[
    '%gmail%',
    '%yahoo%',
    '%google%',
    '%hotmail%',
    '%aol.com%',
    '%outlook%',
    '%icloud%',
    '%tumbler%',
    '%protonmail%',
    '%linkedin%',
    '%facebook%',
    '%twitter%',
    '%youtube%',
    '%instagram%',
    '%vimeo%',
    '%glassdoor%',
    '%tiktok%',
    '%podbean%',
    '%apple%',
    '%soundcloud%',
    '%spotify%',
    '%reddit%',
    '%me.com%',
    '%mac.com%',
    '%live.com%',
    '%msn.com%',
    '%att.com%',
    '%sbcglobal%',
    '%twitter%',
    '%bellsouth%',
    '%verizon%',
    '%cox.net%',
    '%charter.net%',
    '%earthlink%',
    '%juno.com%',
    '%optonline%',
    '%netzero%',
    '%frontiernet%',
    '%windstream%',
    '%suddenlink%',
    '%cableone%',
    '%centurylink%'
]);
