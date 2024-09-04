-- metadata."SecurityMaster" definition

-- Drop table

-- DROP TABLE metadata."SecurityMaster";

CREATE TABLE metadata."SecurityMaster" (
	"Id" text NOT NULL,
	"Permaticker" text NULL,
	"Ticker" text NULL,
	"Name" text NULL,
	"Exchange" text NULL,
	"IsDelisted" text NULL,
	"Category" text NULL,
	"Cusips" text NULL,
	"SicCode" text NULL,
	"SicSector" text NULL,
	"SicIndustry" text NULL,
	"FamaSector" text NULL,
	"FamaIndustry" text NULL,
	"Sector" text NULL,
	"Industry" text NULL,
	"ScaleMarketCap" text NULL,
	"ScaleRevenue" text NULL,
	"RelatedTickers" text NULL,
	"Currency" text NULL,
	"Location" text NULL,
	"LastUpdated" text NULL,
	"FirstAdded" text NULL,
	"FirstPriceDate" text NULL,
	"LastPriceDate" text NULL,
	"FirstQuarter" text NULL,
	"LastQuarter" text NULL,
	"SecFilings" text NULL,
	"CompanySite" text NULL,
	"NGCreatedOn" timestamptz NOT NULL,
	"NGUpdatedOn" timestamptz NOT NULL,
	"NGIsSampleData" bool NOT NULL,
	"NGSampleDataSet" text NULL,
	"NGCreatedBy" text NULL,
	"NGUpdatedBy" text NULL,
	"NGSessionId" text NULL,
	"CompanyDescription" text NULL,
	CONSTRAINT "PK_SecurityMaster" PRIMARY KEY ("Id")
);