CREATE TABLE IF NOT EXISTS "foodbanks"
(
    [FoodBankId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [Name] TEXT  NOT NULL,
    [ItemsNeeded] TEXT,
    [Address] TEXT,
    [ZipCode] INTEGER,
    UNIQUE(Name)
);
CREATE INDEX IF NOT EXISTS [IFK_FoodBankId] ON "foodbanks" ([FoodBankId]);

INSERT OR IGNORE INTO foodbanks (Name, ItemsNeeded, Address, ZipCode)
VALUES
  ('Niagara Falls Food Bank', 'Rice, beans, milk', 'Behind Scott Adams hydro power plant #1, 218 Ontario Ave', 2183),
  ('New York Queens Food Bank', 'Pasta, tinned soup, childrens toys', '134 Brooklyn St', 91083),
  ('Tampa Central Food Bank', 'Tinned fruit, sugar, flour', '2016 Orlando Ave', 70542)
