select distinct p."AccountId" from "Position" p ;

INSERT INTO "Position" (
	"Id",
	"AccountId",
	"CreatedBy",
	"UpdatedBy",
	"CreatedOn",
	"UpdatedOn",
    "SICOffice",
    "SICCode",
    "ExternalSystemKeyCustody",
    "AssetClassLevel1",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyDayCostBasis",
    "BaseCurrencyDayEndAccruedDividendIncome",
    "BaseCurrencyDayEndPriceDate",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyEndMarketValue",
    "BaseCurrencyOriginalUnitCost",
    "BaseCurrencyYTDRealizedDividendIncome",
    "CompanyWebsiteURL",
    "CountryOfIssuance",
    "GICSSector",
    "HasStalePrice",
    "InvestmentType",
    "IsDelisted",
    "LocalCurrencyCode",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "LocalCurrencyEndMarketValue",
    "LocalCurrencyEndPrice",
    "LocalCurrencyOriginalUnitCost",
    "MarketPrice",
    "OtherIndustryLevel2",
    "OtherSectorLevel3",
    "OtherSecurityStrategyLevel1",
    "OtherSecurityStrategyLevel2",
    "PrimaryExchange",
    "RelatedTickers",
    "SECFilingURLs",
    "SecurityLegalName",
    "SICIndustryTitle",
    "SymCusip",
    "SymTicker",
    "UnitsHeld",
    "BrandSymbolURL" 
) VALUES
(
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	'144ea870-8649-46d7-9041-cfcf2486164e',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	now(),
	now(),
	'Cash & Cash Equivalents',                 -- SICOffice
    NULL,                                      -- SICCode
    538776741796,                              -- ExternalSystemKeyCustody
    'Cash & Cash Equivalents',                 -- AssetClassLevel1
    0,                                         -- BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss
    187243.45,                                 -- BaseCurrencyDayCostBasis
    0,                                         -- BaseCurrencyDayEndAccruedDividendIncome
    '2024-06-12 16:30:00',                     -- BaseCurrencyDayEndPriceDate
    0,                                         -- BaseCurrencyDayEndUnrealizedPriceGainLoss
    187243.45,                                 -- BaseCurrencyEndMarketValue
    1,                                         -- BaseCurrencyOriginalUnitCost
    0,                                         -- BaseCurrencyYTDRealizedDividendIncome
    'https://www.usa.gov/',                    -- CompanyWebsiteURL
    'USA',                                     -- CountryOfIssuance
    'Cash & Cash Equivalents',                 -- GICSSector
    FALSE,                                     -- HasStalePrice
    'Cash & Cash Equivalents',                 -- InvestmentType
    'N',                                       -- IsDelisted
    'USD',                                     -- LocalCurrencyCode
    0,                                         -- LocalCurrencyDayEndUnrealizedPriceGainLoss
    187243.45,                                 -- LocalCurrencyEndMarketValue
    1,                                         -- LocalCurrencyEndPrice
    1,                                         -- LocalCurrencyOriginalUnitCost
    1,                                         -- MarketPrice
    'Cash & Cash Equivalents',                 -- OtherIndustryLevel2
    'Cash & Cash Equivalents',                 -- OtherSectorLevel3
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel1
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel2
    'Cash',                                    -- PrimaryExchange
    NULL,                                      -- RelatedTickers
    Null,                                        -- SECFilingURLs
    'Cash & Cash Equivalents',                 -- SecurityLegalName
    'Cash & Cash Equivalents',                 -- SICIndustryTitle
    'USDOLLAR',                                -- SymCusip
    'USDOLLAR',                                -- SymTicker
    187243.45,                                 -- UnitsHeld
    'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/currency-usd.svg'                     -- BrandSymbolURL
);


INSERT INTO "Position" (
	"Id",
	"AccountId",
	"CreatedBy",
	"UpdatedBy",
	"CreatedOn",
	"UpdatedOn",
    "SICOffice",
    "SICCode",
    "ExternalSystemKeyCustody",
    "AssetClassLevel1",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyDayCostBasis",
    "BaseCurrencyDayEndAccruedDividendIncome",
    "BaseCurrencyDayEndPriceDate",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyEndMarketValue",
    "BaseCurrencyOriginalUnitCost",
    "BaseCurrencyYTDRealizedDividendIncome",
    "CompanyWebsiteURL",
    "CountryOfIssuance",
    "GICSSector",
    "HasStalePrice",
    "InvestmentType",
    "IsDelisted",
    "LocalCurrencyCode",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "LocalCurrencyEndMarketValue",
    "LocalCurrencyEndPrice",
    "LocalCurrencyOriginalUnitCost",
    "MarketPrice",
    "OtherIndustryLevel2",
    "OtherSectorLevel3",
    "OtherSecurityStrategyLevel1",
    "OtherSecurityStrategyLevel2",
    "PrimaryExchange",
    "RelatedTickers",
    "SECFilingURLs",
    "SecurityLegalName",
    "SICIndustryTitle",
    "SymCusip",
    "SymTicker",
    "UnitsHeld",
    "BrandSymbolURL" 
) VALUES
(
	'eee903d2-b979-4071-b954-97d9c4894045',
	'6fba0ebd-7ffd-4e11-bb88-e0379f479f01',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	now(),
	now(),
	'Cash & Cash Equivalents',                 -- SICOffice
    NULL,                                      -- SICCode
    538776741796,                              -- ExternalSystemKeyCustody
    'Cash & Cash Equivalents',                 -- AssetClassLevel1
    0,                                         -- BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss
    293852.76,                                 -- BaseCurrencyDayCostBasis
    0,                                         -- BaseCurrencyDayEndAccruedDividendIncome
    '2024-06-12 16:30:00',                     -- BaseCurrencyDayEndPriceDate
    0,                                         -- BaseCurrencyDayEndUnrealizedPriceGainLoss
    293852.76,                                 -- BaseCurrencyEndMarketValue
    1,                                         -- BaseCurrencyOriginalUnitCost
    0,                                         -- BaseCurrencyYTDRealizedDividendIncome
    'https://www.usa.gov/',                    -- CompanyWebsiteURL
    'USA',                                     -- CountryOfIssuance
    'Cash & Cash Equivalents',                 -- GICSSector
    FALSE,                                     -- HasStalePrice
    'Cash & Cash Equivalents',                 -- InvestmentType
    'N',                                       -- IsDelisted
    'USD',                                     -- LocalCurrencyCode
    0,                                         -- LocalCurrencyDayEndUnrealizedPriceGainLoss
    293852.76,                                 -- LocalCurrencyEndMarketValue
    1,                                         -- LocalCurrencyEndPrice
    1,                                         -- LocalCurrencyOriginalUnitCost
    1,                                         -- MarketPrice
    'Cash & Cash Equivalents',                 -- OtherIndustryLevel2
    'Cash & Cash Equivalents',                 -- OtherSectorLevel3
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel1
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel2
    'Cash',                                    -- PrimaryExchange
    NULL,                                      -- RelatedTickers
    Null,                                        -- SECFilingURLs
    'Cash & Cash Equivalents',                 -- SecurityLegalName
    'Cash & Cash Equivalents',                 -- SICIndustryTitle
    'USDOLLAR',                                -- SymCusip
    'USDOLLAR',                                -- SymTicker
    293852.76,                                 -- UnitsHeld
    'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/currency-usd.svg'                     -- BrandSymbolURL
);

INSERT INTO "Position" (
	"Id",
	"AccountId",
	"CreatedBy",
	"UpdatedBy",
	"CreatedOn",
	"UpdatedOn",
    "SICOffice",
    "SICCode",
    "ExternalSystemKeyCustody",
    "AssetClassLevel1",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyDayCostBasis",
    "BaseCurrencyDayEndAccruedDividendIncome",
    "BaseCurrencyDayEndPriceDate",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyEndMarketValue",
    "BaseCurrencyOriginalUnitCost",
    "BaseCurrencyYTDRealizedDividendIncome",
    "CompanyWebsiteURL",
    "CountryOfIssuance",
    "GICSSector",
    "HasStalePrice",
    "InvestmentType",
    "IsDelisted",
    "LocalCurrencyCode",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "LocalCurrencyEndMarketValue",
    "LocalCurrencyEndPrice",
    "LocalCurrencyOriginalUnitCost",
    "MarketPrice",
    "OtherIndustryLevel2",
    "OtherSectorLevel3",
    "OtherSecurityStrategyLevel1",
    "OtherSecurityStrategyLevel2",
    "PrimaryExchange",
    "RelatedTickers",
    "SECFilingURLs",
    "SecurityLegalName",
    "SICIndustryTitle",
    "SymCusip",
    "SymTicker",
    "UnitsHeld",
    "BrandSymbolURL" 
) VALUES
(
	'ad0d5660-e95e-4bc1-99d5-36dd1ab9e724',
	'a1e7aba5-d508-45bf-b129-5d462f2b217d',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	now(),
	now(),
	'Cash & Cash Equivalents',                 -- SICOffice
    NULL,                                      -- SICCode
    538776741796,                              -- ExternalSystemKeyCustody
    'Cash & Cash Equivalents',                 -- AssetClassLevel1
    0,                                         -- BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss
    120372.37,                                 -- BaseCurrencyDayCostBasis
    0,                                         -- BaseCurrencyDayEndAccruedDividendIncome
    '2024-06-12 16:30:00',                     -- BaseCurrencyDayEndPriceDate
    0,                                         -- BaseCurrencyDayEndUnrealizedPriceGainLoss
    120372.37,                                 -- BaseCurrencyEndMarketValue
    1,                                         -- BaseCurrencyOriginalUnitCost
    0,                                         -- BaseCurrencyYTDRealizedDividendIncome
    'https://www.usa.gov/',                    -- CompanyWebsiteURL
    'USA',                                     -- CountryOfIssuance
    'Cash & Cash Equivalents',                 -- GICSSector
    FALSE,                                     -- HasStalePrice
    'Cash & Cash Equivalents',                 -- InvestmentType
    'N',                                       -- IsDelisted
    'USD',                                     -- LocalCurrencyCode
    0,                                         -- LocalCurrencyDayEndUnrealizedPriceGainLoss
    120372.37,                                 -- LocalCurrencyEndMarketValue
    1,                                         -- LocalCurrencyEndPrice
    1,                                         -- LocalCurrencyOriginalUnitCost
    1,                                         -- MarketPrice
    'Cash & Cash Equivalents',                 -- OtherIndustryLevel2
    'Cash & Cash Equivalents',                 -- OtherSectorLevel3
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel1
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel2
    'Cash',                                    -- PrimaryExchange
    NULL,                                      -- RelatedTickers
    Null,                                        -- SECFilingURLs
    'Cash & Cash Equivalents',                 -- SecurityLegalName
    'Cash & Cash Equivalents',                 -- SICIndustryTitle
    'USDOLLAR',                                -- SymCusip
    'USDOLLAR',                                -- SymTicker
    120372.37,                                 -- UnitsHeld
    'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/currency-usd.svg'                     -- BrandSymbolURL
);

INSERT INTO "Position" (
	"Id",
	"AccountId",
	"CreatedBy",
	"UpdatedBy",
	"CreatedOn",
	"UpdatedOn",
    "SICOffice",
    "SICCode",
    "ExternalSystemKeyCustody",
    "AssetClassLevel1",
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss",
    "BaseCurrencyDayCostBasis",
    "BaseCurrencyDayEndAccruedDividendIncome",
    "BaseCurrencyDayEndPriceDate",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss",
    "BaseCurrencyEndMarketValue",
    "BaseCurrencyOriginalUnitCost",
    "BaseCurrencyYTDRealizedDividendIncome",
    "CompanyWebsiteURL",
    "CountryOfIssuance",
    "GICSSector",
    "HasStalePrice",
    "InvestmentType",
    "IsDelisted",
    "LocalCurrencyCode",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss",
    "LocalCurrencyEndMarketValue",
    "LocalCurrencyEndPrice",
    "LocalCurrencyOriginalUnitCost",
    "MarketPrice",
    "OtherIndustryLevel2",
    "OtherSectorLevel3",
    "OtherSecurityStrategyLevel1",
    "OtherSecurityStrategyLevel2",
    "PrimaryExchange",
    "RelatedTickers",
    "SECFilingURLs",
    "SecurityLegalName",
    "SICIndustryTitle",
    "SymCusip",
    "SymTicker",
    "UnitsHeld",
    "BrandSymbolURL" 
) VALUES
(
	'5e249108-7cdf-4ba2-9a98-9318ecf0b8a1',
	'a6185f24-082b-41f6-a529-a31f7d2cce86',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	'b88c8f0c-e4ec-4142-b1af-3d81cffdf143Id',
	now(),
	now(),
	'Cash & Cash Equivalents',                 -- SICOffice
    NULL,                                      -- SICCode
    538776741796,                              -- ExternalSystemKeyCustody
    'Cash & Cash Equivalents',                 -- AssetClassLevel1
    0,                                         -- BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss
    83092.34,                                 -- BaseCurrencyDayCostBasis
    0,                                         -- BaseCurrencyDayEndAccruedDividendIncome
    '2024-06-12 16:30:00',                     -- BaseCurrencyDayEndPriceDate
    0,                                         -- BaseCurrencyDayEndUnrealizedPriceGainLoss
    83092.34,                                 -- BaseCurrencyEndMarketValue
    1,                                         -- BaseCurrencyOriginalUnitCost
    0,                                         -- BaseCurrencyYTDRealizedDividendIncome
    'https://www.usa.gov/',                    -- CompanyWebsiteURL
    'USA',                                     -- CountryOfIssuance
    'Cash & Cash Equivalents',                 -- GICSSector
    FALSE,                                     -- HasStalePrice
    'Cash & Cash Equivalents',                 -- InvestmentType
    'N',                                       -- IsDelisted
    'USD',                                     -- LocalCurrencyCode
    0,                                         -- LocalCurrencyDayEndUnrealizedPriceGainLoss
    83092.34,                                 -- LocalCurrencyEndMarketValue
    1,                                         -- LocalCurrencyEndPrice
    1,                                         -- LocalCurrencyOriginalUnitCost
    1,                                         -- MarketPrice
    'Cash & Cash Equivalents',                 -- OtherIndustryLevel2
    'Cash & Cash Equivalents',                 -- OtherSectorLevel3
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel1
    'Cash & Cash Equivalents',                 -- OtherSecurityStrategyLevel2
    'Cash',                                    -- PrimaryExchange
    NULL,                                      -- RelatedTickers
    Null,                                        -- SECFilingURLs
    'Cash & Cash Equivalents',                 -- SecurityLegalName
    'Cash & Cash Equivalents',                 -- SICIndustryTitle
    'USDOLLAR',                                -- SymCusip
    'USDOLLAR',                                -- SymTicker
    83092.34,                                 -- UnitsHeld
    'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/currency-usd.svg'                     -- BrandSymbolURL
);


