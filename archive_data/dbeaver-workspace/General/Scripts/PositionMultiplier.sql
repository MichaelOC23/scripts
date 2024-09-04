
select * from metadata."Account" a;

select "Id", "ShortName" from metadata."Account" a;

select "BaseCurrencyEndMarketValue" from platform.metadata."Position" p where "AccountId" ='a6185f24-082b-41f6-a529-a31f7d2cce86';


update metadata."PrivateAsset"  set "CreatedBy" = '3c8ff3e3-112c-4cd0-a0ca-2c289a0583da'where "RecordContext" ='WATCHLIST';


select "Id", "AcquisitionDate", "AcquisitionCost", "UnitsHeld", "SymTicker", "CreatedBy", "CreatedOn", "UpdatedBy", "UpdatedOn", "RecordContext"  from metadata."PrivateAsset" pa where pa."RecordContext" = 'WATCHLIST';

update metadata."Account" set "ShortName" = 'Private Assets' where "Id"  = '7cef2113-8129-49db-add5-bf10412ae218';
update metadata."Account" set "ShortName" = 'Checking' where "Id"  = 'ec78801a-320c-40f6-8da9-6bc7c0d624f8';
update metadata."Account" set "ShortName" = 'Operating Cash' where "Id"  = '3f2dae2a-adcc-48fc-9f39-7013f69b4eee';
update metadata."Account" set "ShortName" = 'Other Assets' where "Id"  = '028603f1-86fd-4c5f-80c5-5968c42e6609';
update metadata."Account" set "ShortName" = 'General Savings' where "Id"  = '743e33ed-77fe-48dd-b022-42f4b702d670';
update metadata."Account" set "ShortName" = 'Large Cap Tax Efficient' where "Id"  = 'a6185f24-082b-41f6-a529-a31f7d2cce86';
update metadata."Account" set "ShortName" = 'ROTH IRA' where "Id"  = '144ea870-8649-46d7-9041-cfcf2486164e';
update metadata."Account" set "ShortName" = 'Traditional IRA' where "Id"  = '6fba0ebd-7ffd-4e11-bb88-e0379f479f01';
update metadata."Account" set "ShortName" = 'International Equity' where "Id"  = 'a1e7aba5-d508-45bf-b129-5d462f2b217d';
update metadata."Account" set "ShortName" = 'Car Collection' where "Id"  = 'd6f8f94d-1a45-40c3-88d9-8ea70f949b84';
update metadata."Account" set "ShortName" = 'Hourses' where "Id"  = '26b89093-ead2-4ec8-b2e8-d835b204e962';
update metadata."Account" set "ShortName" = 'Jevelry Collection' where "Id"  = '261128c5-a19f-46ee-b9e9-3b3a95bb99d5';
update metadata."Account" set "ShortName" = 'Art Collection' where "Id"  = 'ce703466-cc8d-458c-a3ab-4dddcc8e19b0';



--Updates to the Account Table
select * from metadata."Account";
update metadata."Account" set "ShortName" = 'Checking' where "AccountNumber"  = '41607966006';

update metadata."Account" set "ShortName" = 'Operating Cash' where "AccountNumber"  = '30854145052';


-- Updates to CASH POSITION in Position Table
select * from metadata."Position" p where "AccountId" = 'a6185f24-082b-41f6-a529-a31f7d2cce86' ;
select p."AccountId", a."ShortName"  from metadata."Position" p, metadata."Account" a where p."AccountId" = a."Id" and ;
select p."AccountId", a."ShortName",  p."BaseCurrencyDayCostBasis", p."BaseCurrencyEndMarketValue", p."BaseCurrencyOriginalUnitCost", p."LocalCurrencyEndMarketValue", p."UnitsHeld" from metadata."Position" p, metadata."Account" a where  p."AccountId" = a."Id" and p."AccountId"  in ('ec78801a-320c-40f6-8da9-6bc7c0d624f8', '3f2dae2a-adcc-48fc-9f39-7013f69b4eee', '743e33ed-77fe-48dd-b022-42f4b702d670');

	
	--Checking Update
	update metadata."Position" set 
	"BaseCurrencyDayCostBasis" = 	300177, 
	"BaseCurrencyEndMarketValue" = 300177,
	"LocalCurrencyEndMarketValue" = 300177,
	"UnitsHeld" = 300177
	where "AccountId" = 'ec78801a-320c-40f6-8da9-6bc7c0d624f8';
	
	--General Savings Update
	update metadata."Position"  set 
	"BaseCurrencyDayCostBasis" = 	284340, 
	"BaseCurrencyEndMarketValue" = 284340,
	"LocalCurrencyEndMarketValue" = 284340,
	"UnitsHeld" = 284340
	where "AccountId" = '743e33ed-77fe-48dd-b022-42f4b702d670';
	
	
	--Operating Cash Update 
	update metadata."Position"  set 
	"BaseCurrencyDayCostBasis" = 	1409075, 
	"BaseCurrencyEndMarketValue" = 1409075,
	"LocalCurrencyEndMarketValue" = 1409075,
	"UnitsHeld" = 1409075
	where "AccountId" = '3f2dae2a-adcc-48fc-9f39-7013f69b4eee';


-- Updates to Position Values

select * from "Position" p;


select p."AccountId", a."ShortName", a."GeneralLedgerType", p."SymTicker" 
	"BaseCurrencyEndMarketValue", 
	"LocalCurrencyEndMarketValue",
	"BaseCurrencyDayEndUnrealizedPriceGainLoss",
	"BaseCurrencyDayEndAccruedDividendIncome",
	"BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
	"BaseCurrencyYTDRealizedDividendIncome",
	"LocalCurrencyDayEndUnrealizedPriceGainLoss",
	"BaseCurrencyDayCostBasis",
	"BaseCurrencyOriginalUnitCost",
	"LocalCurrencyOriginalUnitCost",
	"UnitsHeld"
from metadata."Position" p, metadata."Account" a
where p."AccountId" = a."Id" ;

and p."AccountId" ='a6185f24-082b-41f6-a529-a31f7d2cce86';

and p."AccountId" not in  ('ec78801a-320c-40f6-8da9-6bc7c0d624f8', '3f2dae2a-adcc-48fc-9f39-7013f69b4eee', '743e33ed-77fe-48dd-b022-42f4b702d670');


select p."AccountId", a."ShortName", 
	count(p."Id"),
	sum(p."BaseCurrencyEndMarketValue"), 
	sum(p."LocalCurrencyEndMarketValue"),
	sum(p."BaseCurrencyDayEndUnrealizedPriceGainLoss"),
	sum(p."BaseCurrencyDayEndAccruedDividendIncome"),
	sum(p."BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss"),
	sum(p."BaseCurrencyYTDRealizedDividendIncome"),
	sum(p."LocalCurrencyDayEndUnrealizedPriceGainLoss"),
	sum(p."BaseCurrencyDayCostBasis"),
	sum(p."BaseCurrencyOriginalUnitCost"),
	sum(p."LocalCurrencyOriginalUnitCost"),
	sum(p."UnitsHeld")
	FROM metadata."Position" p, metadata."Account" a 
	WHERE p."AccountId" = a."Id" and p."AccountId" not in  ('ec78801a-320c-40f6-8da9-6bc7c0d624f8', '3f2dae2a-adcc-48fc-9f39-7013f69b4eee', '743e33ed-77fe-48dd-b022-42f4b702d670')
	group by p."AccountId", a."ShortName";







--144ea870-8649-46d7-9041-cfcf2486164e	ROTH IRA
--6fba0ebd-7ffd-4e11-bb88-e0379f479f01	Traditional IRA 
--a1e7aba5-d508-45bf-b129-5d462f2b217d	International Equity
--a6185f24-082b-41f6-a529-a31f7d2cce86	Large Cap Tax Efficient




--144ea870-8649-46d7-9041-cfcf2486164e	ROTH IRA
WITH factor AS (
    SELECT  .853692::numeric AS value -- replace 2.0 with your desired factor
)
UPDATE metadata."Position"
SET 
    "BaseCurrencyEndMarketValue" = (SELECT value FROM factor) * "BaseCurrencyEndMarketValue", 
    "LocalCurrencyEndMarketValue" = (SELECT value FROM factor) * "LocalCurrencyEndMarketValue",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyYTDRealizedDividendIncome" = (SELECT value FROM factor) * "BaseCurrencyYTDRealizedDividendIncome",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayCostBasis" = (SELECT value FROM factor) * "BaseCurrencyDayCostBasis",
    "BaseCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "BaseCurrencyOriginalUnitCost",
    "LocalCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "LocalCurrencyOriginalUnitCost",
    "UnitsHeld" = (SELECT value FROM factor) * "UnitsHeld",
     "updatedby" = 'your_user_id', -- replace 'your_user_id' with the actual user id
    "updatedon" = NOW()
WHERE "AccountId" = '144ea870-8649-46d7-9041-cfcf2486164e';



--6fba0ebd-7ffd-4e11-bb88-e0379f479f01	Traditional IRA 
WITH factor AS (
    SELECT  .853692::numeric AS value -- replace 2.0 with your desired factor
)
UPDATE metadata."Position"
SET 
    "BaseCurrencyEndMarketValue" = (SELECT value FROM factor) * "BaseCurrencyEndMarketValue", 
    "LocalCurrencyEndMarketValue" = (SELECT value FROM factor) * "LocalCurrencyEndMarketValue",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyYTDRealizedDividendIncome" = (SELECT value FROM factor) * "BaseCurrencyYTDRealizedDividendIncome",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayCostBasis" = (SELECT value FROM factor) * "BaseCurrencyDayCostBasis",
    "BaseCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "BaseCurrencyOriginalUnitCost",
    "LocalCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "LocalCurrencyOriginalUnitCost",
    "UnitsHeld" = (SELECT value FROM factor) * "UnitsHeld"
WHERE "AccountId" = '6fba0ebd-7ffd-4e11-bb88-e0379f479f01';



--a1e7aba5-d508-45bf-b129-5d462f2b217d	International Equity
WITH factor AS (
    SELECT  .853692::numeric AS value -- replace 2.0 with your desired factor
)
UPDATE metadata."Position"
SET 
    "BaseCurrencyEndMarketValue" = (SELECT value FROM factor) * "BaseCurrencyEndMarketValue", 
    "LocalCurrencyEndMarketValue" = (SELECT value FROM factor) * "LocalCurrencyEndMarketValue",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyYTDRealizedDividendIncome" = (SELECT value FROM factor) * "BaseCurrencyYTDRealizedDividendIncome",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayCostBasis" = (SELECT value FROM factor) * "BaseCurrencyDayCostBasis",
    "BaseCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "BaseCurrencyOriginalUnitCost",
    "LocalCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "LocalCurrencyOriginalUnitCost",
    "UnitsHeld" = (SELECT value FROM factor) * "UnitsHeld"
WHERE "AccountId" = 'a1e7aba5-d508-45bf-b129-5d462f2b217d';




--a6185f24-082b-41f6-a529-a31f7d2cce86	Large Cap Tax Efficient
WITH factor AS (
    SELECT  .853692::numeric AS value -- replace 2.0 with your desired factor
)
UPDATE metadata."Position"
SET 
    "BaseCurrencyEndMarketValue" = (SELECT value FROM factor) * "BaseCurrencyEndMarketValue", 
    "LocalCurrencyEndMarketValue" = (SELECT value FROM factor) * "LocalCurrencyEndMarketValue",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss" = (SELECT value FROM factor) * "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyYTDRealizedDividendIncome" = (SELECT value FROM factor) * "BaseCurrencyYTDRealizedDividendIncome",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss" = (SELECT value FROM factor) * "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyDayCostBasis" = (SELECT value FROM factor) * "BaseCurrencyDayCostBasis",
    "BaseCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "BaseCurrencyOriginalUnitCost",
    "LocalCurrencyOriginalUnitCost" = (SELECT value FROM factor) * "LocalCurrencyOriginalUnitCost",
    "UnitsHeld" = (SELECT value FROM factor) * "UnitsHeld"
WHERE "AccountId" = 'a6185f24-082b-41f6-a529-a31f7d2cce86';



select a."ShortName", sum(p."BaseCurrencyEndMarketValue") from metadata."Position" p, metadata."Account" a where a."Id"=p."AccountId" and "AccountId" = 'a6185f24-082b-41f6-a529-a31f7d2cce86'group by  a."ShortName";


select u."Id" from metadata."User" u where u."Email" ilike '%product%';
