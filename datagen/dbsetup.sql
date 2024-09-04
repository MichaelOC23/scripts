 CREATE TABLE datagen."CodeSet" (
                        "Id" char(36) NOT NULL,
                        "Source" text NOT NULL,
                        "Description" text NOT NULL,
                        "Code" text NOT NULL,
                        "Category" text NULL,
                        "CodeValueString1" text NULL,
                        "CodeValueString2" text NULL,
                        "CodeValueString3" text NULL,
                        "CodeValueFloat1" float4 NULL,
                        "CodeValueDate1" timestamptz NULL,
                        "CodeValueInt1" int4 NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedOn" timestamptz NOT NULL,
                        "CreatedBy" text NULL,
                        "UpdatedBy" text NULL,
                        CONSTRAINT "PK_CodeSet" PRIMARY KEY ("Id")
                    );

                    CREATE TABLE datagen."PriceHistory" (
                        "Id" char(36) NOT NULL,
                        "Ticker" text NOT NULL,
                        "LastUpdated" timestamptz NOT NULL,
                        "AsOfDate" timestamptz NOT NULL,
                        "EnterpriseValueDaily" numeric NULL,
                        "MarketCapitalization" numeric NULL,
                        "PriceToBookValue" numeric NULL,
                        "PriceEarningsRatio" numeric NULL,
                        "PriceSalesRatio" numeric NULL,
                        "CreatedBy" text NOT NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedBy" text NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "DeletedBy" text NULL,
                        CONSTRAINT "PK_PriceHistory" PRIMARY KEY ("Id")
                    );

                    CREATE TABLE datagen."SecurityMaster" (
                        "Id" char(36) NOT NULL,
                        "AssetClassLevel1" text NOT NULL,
                        "AssetClassLevel2" text NULL,
                        "AssetClassLevel3" text NULL,
                        "BrandSymbolURL" text NULL,
                        "CompanyDescription" text NULL,
                        "CompanyWebsiteURL" text NULL,
                        "CountryOfIssuance" text NULL,
                        "CountryOfRisk" text NULL,
                        "CouponRate" numeric NULL,
                        "CreditRating" text NULL,
                        "CurrencyCode" text NOT NULL,
                        "CurrentYield" numeric NULL,
                        "DividendPaymentFrequency" text NULL,
                        "DividendYield" numeric NULL,
                        "ExchangeCode" text NULL,
                        "ExpirationDate" text NULL,
                        "ExternalSystemKeySecurityGoldCopy" text NULL,
                        "FaceValue" numeric NULL,
                        "FactSheetURL" text NULL,
                        "FitchRating" text NULL,
                        "GICSIndustry" text NULL,
                        "GICSIndustryGroup" text NULL,
                        "GICSSector" text NULL,
                        "GICSSubIndustry" text NULL,
                        "InceptionDate" text NULL,
                        "InvestmentType" text NULL,
                        "IssuerCategory" text NULL,
                        "IssuerName" text NULL,
                        "MarketPrice" numeric NULL,
                        "MaturityDate" text NULL,
                        "MoodysRating" text NULL,
                        "NasdaqEarliestFinancialQuarter" text NULL,
                        "NasdaqEarliestPriceDate" text NULL,
                        "NasdaqLatestFinancialQuarter" text NULL,
                        "NasdaqMostRecentPriceDate" text NULL,
                        "PriceFactor" numeric NULL,
                        "PricingVendorPrimary" text NULL,
                        "PricingVendorSecondary" text NULL,
                        "PricingVendorTertiary" text NULL,
                        "PrimaryExchange" text NULL,
                        "RegionOfRisk" text NULL,
                        "RelatedTickers" _text NULL,
                        "SECFilingURLs" _text NULL,
                        "SecurityFriendlyName" text NULL,
                        "SecurityLegalName" text NOT NULL,
                        "SecurityShortName" text NULL,
                        "SharesOutstanding" numeric NULL,
                        "SymCusip" text NULL,
                        "SymIsin" text NULL,
                        "SymSedol" text NULL,
                        "SymTicker" text NULL,
                        "YieldToMaturity" numeric NULL,
                        "CreatedBy" text NOT NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedBy" text NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "DeletedBy" text NULL,
                        CONSTRAINT "PK_SecurityMaster" PRIMARY KEY ("Id")
                    );

                    CREATE TABLE datagen."Account" (
                        "Id" char(36) NOT NULL,
                        "AccountNumber" text NULL,
                        "ExternalSystemKeyAccounting" text NULL,
                        "LegalName" text NULL,
                        "ShortName" text NOT NULL,
                        "LongName" text NULL,
                        "OwnerFriendlyName" text NULL,
                        "ManagerFriendlyName" text NULL,
                        "BaseCurrency" text NULL,
                        "ReportingCurrency" text NULL,
                        "PreferredSecurityIdentifier" text NULL,
                        "AccountOwnerName" text NULL,
                        "AccountOwnerNameJoint" text NULL,
                        "AccountTypes" _text NULL,
                        "InstitutionName1" text NULL,
                        "BusinessUnitLevel1" text NULL,
                        "IsClosed" bool NULL,
                        "AccountCloseDate" text NULL,
                        "CloseReason" text NULL,
                        "AdvisorName" text NULL,
                        "AdvisoryTeamName" text NULL,
                        "ManagerStrategyDescription" text NULL,
                        "TaxTreatmentTypes" _text NULL,
                        "ModelPortfolioName" text NULL,
                        "AssetAllocationName" text NULL,
                        "LotReliefMethodDefault" text NULL,
                        "IsDiscretionary" bool NULL,
                        "OwnerFiscalYearStartDate" text NULL,
                        "IsMasterAccount" bool NULL,
                        "IsSubAccount" bool NULL,
                        "OwnerCountryOfDomicile" text NULL,
                        "AnnualManagementFeePercent" numeric NULL,
                        "Description" text NULL,
                        "IsMarginApproved" bool NULL,
                        "IsOptionsApproved" bool NULL,
                        "TargetMarketValue" numeric NULL,
                        "TargetMarketValueDate" text NULL,
                        "IsExcludedFromRegulatoryReporting" bool NULL,
                        "IsExcludedFromNetWorthReporting" bool NULL,
                        "IsHiddenFromOwner" bool NULL,
                        "IsHiddenFromAdvisor" bool NULL,
                        "IsOwnerDefaultAccount" bool NULL,
                        "IsAdvisorDefaultAccount" bool NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "IsPrivateAsset" bool NULL,
                        "CreatedBy" char(36) NOT NULL,
                        "UpdatedBy" char(36) NOT NULL,
                        "DeletedBy" char(36) NOT NULL,
                        CONSTRAINT "PK_Account_Id" PRIMARY KEY ("Id")
                    );

                    CREATE TABLE datagen."Position" (
                    "Id" char(36) NOT NULL,
                        "AccountId" char(36) NOT NULL,
                        "SecurityId" text NOT NULL,
                        "AssetClassLevel1" text NOT NULL,
                        "AssetClassLevel2" text NULL,
                        "EventLogId" char(36) NOT NULL,
                        "SymCusip" text NULL,
                        "SymIsin" text NULL,
                        "SymTicker" text NULL,
                        "SymSedol" text NULL,
                        "SecurityShortName" text NULL,
                        "SecurityLegalName" text NOT NULL,
                        "LocalCurrencyCode" text NULL,
                        "CountryOfIssuance" text NULL,
                        "CountryOfRisk" text NULL,
                        "RegionOfRisk" text NULL,
                        "InvestmentType" text NULL,
                        "IssuerCategory" text NULL,
                        "IssuerName" text NULL,
                        "ExchangeCode" text NULL,
                        "PrimaryExchange" text NULL,
                        "CreditRating" text NULL,
                        "ExpirationDate" text NULL,
                        "MaturityDate" text NULL,
                        "SharesOutstanding" numeric NULL,
                        "UnitsHeld" numeric NULL,
                        "BaseCurrencyCode" text NULL,
                        "BaseCurrencyEndMarketValue" numeric NULL,
                        "LocalCurrencyEndMarketValue" numeric NULL,
                        "BaseCurrencyDayEndUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyDayChangeUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyDayStartUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyMTDChangeUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyQTDChangeUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyYTDChangeUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyITDChangeUnrealizedPriceGainLoss" numeric NULL,
                        "BaseCurrencyOriginalCost" numeric NULL,
                        "BaseCurrencyOriginalUnitCost" numeric NULL,
                        "BaseCurrencyDayEndPrice" numeric NULL,
                        "BaseCurrencyPriorDayEndPrice" numeric NULL,
                        "MarketPrice" numeric NULL,
                        "PriceFactor" numeric NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "CreatedBy" char(36) NOT NULL,
                        "UpdatedBy" char(36) NOT NULL,
                        "DeletedBy" char(36) NOT NULL,
                        CONSTRAINT "PK_Position_Id" PRIMARY KEY ("Id")
                    );

                    CREATE TABLE datagen."Transaction" (
                        "Id" char(36) NOT NULL,
                        "AccountId" char(36) NOT NULL,
                        "SecurityId" char(36) NOT NULL,
                        "TransactionType" text NOT NULL,
                        "TradeDate" timestamptz NOT NULL,
                        "SettlementDate" timestamptz NULL,
                        "Quantity" numeric NULL,
                        "Price" numeric NULL,
                        "GrossAmount" numeric NOT NULL,
                        "NetAmount" numeric NOT NULL,
                        "Fees" numeric NULL,
                        "Taxes" numeric NULL,
                        "CurrencyCode" text NOT NULL,
                        "ExchangeRate" numeric NULL,
                        "CounterpartyIdentifier" text NULL,
                        "Description" text NULL,
                        "RelatedTransactionId" char(36) NOT NULL,
                        "IsReversed" boolean NOT NULL DEFAULT false,
                        "ReversalTransactionId" char(36) NOT NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "CreatedBy" char(36) NOT NULL,
                        "UpdatedBy" char(36) NOT NULL,
                        "DeletedBy" char(36) NOT NULL,
                        CONSTRAINT "PK_Transaction" PRIMARY KEY ("Id"),
                        -- CONSTRAINT "FK_Transaction_Account" FOREIGN KEY ("AccountId") REFERENCES datagen."Account" ("Id"),
                        -- CONSTRAINT "FK_Transaction_SecurityMaster" FOREIGN KEY ("SecurityId") REFERENCES datagen."SecurityMaster" ("Id")
                        );

                        -- Create an index on the AccountId for faster querying
                        CREATE INDEX "IX_Transaction_AccountId" ON datagen."Transaction" ("AccountId");

                        -- Create an index on the TransactionType for faster filtering
                        CREATE INDEX "IX_Transaction_TransactionType" ON datagen."Transaction" ("TransactionType");

                        -- Create an index on the TradeDate for faster date-based querying
                        CREATE INDEX "IX_Transaction_TradeDate" ON datagen."Transaction" ("TradeDate");


                    INSERT INTO datagen."CodeSet" 

                            ("Id", "Source", "Description", "Code", "Category", "CodeValueString1", "NGCreatedOn", "NGUpdatedOn", "NGCreatedBy", "NGUpdatedBy")
                        VALUES 
                            ('TT001', 'TransactionType', 'Purchase of securities', 'Buy', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT002', 'TransactionType', 'Sale of securities', 'Sell', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT003', 'TransactionType', 'Addition of cash or securities to the portfolio', 'Contribution', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT004', 'TransactionType', 'Removal of cash or securities from the portfolio', 'Withdrawal', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT005', 'TransactionType', 'Cash distribution to shareholders', 'DividendDeclaration', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT006', 'TransactionType', 'Reinvestment of dividends into additional shares', 'DividendReinvestment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT007', 'TransactionType', 'Increase in the number of shares, reducing the price per share', 'StockSplit', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT008', 'TransactionType', 'Decrease in the number of shares, increasing the price per share', 'ReverseStockSplit', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT009', 'TransactionType', 'Distribution of realized capital gains to shareholders', 'CapitalGainDistribution', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT010', 'TransactionType', 'Interest earned on cash or fixed-income securities', 'InterestIncome', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT011', 'TransactionType', 'Payment of interest on a margin loan or other liabilities', 'InterestPayment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT012', 'TransactionType', 'Interest charged on borrowed funds for margin accounts', 'MarginInterest', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT013', 'TransactionType', 'Distribution that reduces the cost basis of the investment', 'ReturnOfCapital', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT014', 'TransactionType', 'Payment of dividends from the portfolio''s securities', 'DividendPayment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT015', 'TransactionType', 'Payment of fees, such as management or advisory fees', 'FeePayment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT016', 'TransactionType', 'Payment of taxes from the portfolio', 'TaxPayment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT017', 'TransactionType', 'Any corporate action not specifically defined', 'OtherCorporateAction', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT018', 'TransactionType', 'Combination of two companies, affecting shareholdings', 'Merger', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT019', 'TransactionType', 'Purchase of one company by another', 'Acquisition', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT020', 'TransactionType', 'Distribution of shares in a subsidiary to existing shareholders', 'SpinOff', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT021', 'TransactionType', 'Offering of additional shares to existing shareholders', 'RightsIssue', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT022', 'TransactionType', 'Offer to purchase shares from shareholders at a specified price', 'TenderOffer', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT023', 'TransactionType', 'Distribution of additional shares instead of cash dividends', 'StockDividend', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT024', 'TransactionType', 'Repurchase of shares by the issuing company', 'StockBuyback', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT025', 'TransactionType', 'Sale of borrowed securities with intention to repurchase later at a lower price', 'ShortSale', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT026', 'TransactionType', 'Purchase of securities to close out a short position', 'ShortCover', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT027', 'TransactionType', 'Transfer of securities into the portfolio', 'TransferIn', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT028', 'TransactionType', 'Transfer of securities out of the portfolio', 'TransferOut', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT029', 'TransactionType', 'Sale of securities to close out the portfolio', 'Liquidation', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT030', 'TransactionType', 'Deposit of cash into the portfolio', 'CashDeposit', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT031', 'TransactionType', 'Withdrawal of cash from the portfolio', 'CashWithdrawal', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT032', 'TransactionType', 'Adjustment to the cost basis of specific tax lots', 'TaxLotAdjustment', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT033', 'TransactionType', 'Sale and repurchase triggering wash sale rules', 'WashSale', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT034', 'TransactionType', 'Corporate restructuring that affects the securities', 'Reorganization', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT035', 'TransactionType', 'Conversion of one type of security into another', 'SecurityConversion', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT036', 'TransactionType', 'Sale of fractional shares', 'FractionalShareSale', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT037', 'TransactionType', 'Fee charged by the custodian for holding securities', 'CustodianFee', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                            ('TT038', 'TransactionType', 'Sale of securities due to a margin call or other requirement', 'ForcedSale', 'Transaction', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System');


                    INSERT INTO datagen."CodeSet" 
                        ("Id", "Source", "Description", "Code", "Category", "CodeValueString1", "NGCreatedOn", "NGUpdatedOn", "NGCreatedBy", "NGUpdatedBy")
                        VALUES 
                        ('OT001', 'OrderType', 'Purchase of securities', 'Buy', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OT002', 'OrderType', 'Sale of securities', 'Sell', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OT003', 'OrderType', 'Addition of cash or securities to the portfolio', 'Contribution', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OT004', 'OrderType', 'Removal of cash or securities from the portfolio', 'Withdrawal', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System');


                    INSERT INTO datagen."CodeSet" 
                        ("Id", "Source", "Description", "Code", "Category", "CodeValueString1", "NGCreatedOn", "NGUpdatedOn", "NGCreatedBy", "NGUpdatedBy")
                        VALUES 
                        ('OS001', 'OrderStatus', 'Order has been received but not yet processed', 'Pending', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OS002', 'OrderStatus', 'Order has been successfully executed', 'Executed', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OS003', 'OrderStatus', 'Order has been cancelled', 'Cancelled', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OS004', 'OrderStatus', 'Order is partially executed', 'PartiallyExecuted', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System'),
                        ('OS005', 'OrderStatus', 'Order execution has failed', 'Failed', 'Order', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System', 'System');


                    CREATE TABLE datagen."Order" (
                        "Id" char(36) NOT NULL,
                        "AccountId" char(36) NOT NULL,
                        "SecurityId" text NULL,
                        "OrderType" text NOT NULL,
                        "OrderStatus" text NOT NULL,
                        "OrderDate" timestamptz NOT NULL,
                        "SettlementDate" timestamptz NULL,
                        "Quantity" numeric NULL,
                        "Price" numeric NULL,
                        "TotalAmount" numeric NOT NULL,
                        "CurrencyCode" text NOT NULL,
                        "ExchangeRate" numeric NULL,
                        "Description" text NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        "UpdatedOn" timestamptz NULL,
                        "DeletedOn" timestamptz NULL,
                        "CreatedBy" char(36) NOT NULL,
                        "UpdatedBy" char(36) NOT NULL,
                        "DeletedBy" char(36) NOT NULL,
                        CONSTRAINT "PK_Order" PRIMARY KEY ("Id")
                        -- CONSTRAINT "FK_Order_Account" FOREIGN KEY ("AccountId") REFERENCES datagen."Account" ("Id"),
                        -- CONSTRAINT "FK_Order_SecurityMaster" FOREIGN KEY ("SecurityId") REFERENCES datagen."SecurityMaster" ("Id")
                            );

                            -- Create an index on the AccountId for faster querying
                            CREATE INDEX "IX_Order_AccountId" ON datagen."Order" ("AccountId");

                            -- Create an index on the OrderType for faster filtering
                            CREATE INDEX "IX_Order_OrderType" ON datagen."Order" ("OrderType");

                            -- Create an index on the OrderDate for faster date-based querying
                            CREATE INDEX "IX_Order_OrderDate" ON datagen."Order" ("OrderDate");

                            -- Create an index on the OrderStatus for faster status-based querying
                            CREATE INDEX "IX_Order_OrderStatus" ON datagen."Order" ("OrderStatus");


                    CREATE TABLE datagen."TaxLot" (
                        "Id" char(36) NOT NULL,
                        "BusinessLotId" char(36) NOT NULL,
                        "AccountId" char(36) NOT NULL,
                        "SecurityId" text NOT NULL,
                        "TransactionId" char(36) NOT NULL,
                        "BusinessDate" timestamptz NOT NULL,
                        "LotMethod" text NOT NULL,
                        "OriginalQuantity" numeric NOT NULL,
                        "RemainingQuantity" numeric NOT NULL,
                        "CostBasis" numeric NOT NULL,
                        "OriginalUnitCost" numeric NOT NULL,
                        "AccrualLedgerCode" text NULL,
                        "AccrualDebit" numeric NULL,
                        "AccrualCredit" numeric NULL,
                    "ParentLotId" char(36) NULL,
                        "EventLogId" char(36) NOT NULL,
                        "LastRecalculatedOn" timestamptz NOT NULL,
                        "DeprecatedOn" timestamptz NULL,
                        "CreatedOn" timestamptz NOT NULL,
                        CONSTRAINT "PK_TaxLot" PRIMARY KEY ("Id")
                        -- CONSTRAINT "FK_TaxLot_Account" FOREIGN KEY ("AccountId") REFERENCES datagen."Account" ("Id"),
                        -- CONSTRAINT "FK_TaxLot_SecurityMaster" FOREIGN KEY ("SecurityId") REFERENCES datagen."SecurityMaster" ("Id"),
                        -- CONSTRAINT "FK_TaxLot_Transaction" FOREIGN KEY ("TransactionId") REFERENCES datagen."Transaction" ("Id"),
                        -- CONSTRAINT "FK_TaxLot_ParentLot" FOREIGN KEY ("ParentLotId") REFERENCES datagen."TaxLot" ("Id"),
                        -- CONSTRAINT "FK_TaxLot_EventLog" FOREIGN KEY ("EventLogId") REFERENCES datagen."EventLog" ("Id")
                    );

                        -- Create indexes for faster querying
                        CREATE INDEX "IX_TaxLot_AccountId" ON datagen."TaxLot" ("AccountId");
                        CREATE INDEX "IX_TaxLot_SecurityId" ON datagen."TaxLot" ("SecurityId");
                        CREATE INDEX "IX_TaxLot_TransactionId" ON datagen."TaxLot" ("TransactionId");
                        CREATE INDEX "IX_TaxLot_BusinessDate" ON datagen."TaxLot" ("BusinessDate");
                        CREATE INDEX "IX_TaxLot_DeprecatedOn" ON datagen."TaxLot" ("DeprecatedOn");
                        
                        INSERT INTO datagen."EventLog" 
                            ("Id", "EventType", "EventDescription", "EventDate", "RelatedEntityId", "RelatedEntityType")
                            VALUES 
                            (
                            gen_random_uuid(), -- Generates a new UUID for the Id
                            'DatabaseSetup',
                            'Initial database schema creation completed - Version 1.0',
                            CURRENT_TIMESTAMP,
                            NULL, -- No specific entity is related
                            NULL  -- No specific entity type
                        ); 