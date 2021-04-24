CREATE TABLE trade(
   id INTEGER PRIMARY KEY,
   pair TEXT,
   type TEXT,
   qty NUMERIC,
   price NUMERIC,
   total NUMERIC,
   date DATETIME,
   fee NUMERIC,
   fee_asset TEXT,
   origin_id TEXT,
   origin TEXT
);

CREATE INDEX trade_id_index ON trade (id ASC);
