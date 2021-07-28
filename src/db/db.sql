-- wallet
DROP TABLE IF EXISTS wallet;

CREATE TABLE wallet(
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE INDEX wallet_id_index ON wallet (id ASC);

-- trade

DROP TABLE IF EXISTS trade;

CREATE TABLE trade(
    id INTEGER PRIMARY KEY,
    id_wallet INTEGER REFERENCES wallet (id),
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

CREATE TABLE asset_wallet(
    id INTEGER PRIMARY KEY,
    id_wallet INTEGER REFERENCES wallet(id)
    asset TEXT,
    qty NUMERIC,
    pru NUMERIC,
    currency TEXT
);

CREATE INDEX trade_id_index ON trade (id ASC);

-- pnl

DROP TABLE IF EXISTS pnl;

CREATE TABLE pnl(
    id INTEGER PRIMARY KEY,
    id_wallet INTEGER REFERENCES wallet (id),
    date DATETIME,
    asset TEXT,
    value NUMERIC,
    currency TEXT
);

CREATE INDEX pnl_id_index ON pnl (id ASC);


-- total_pnl

DROP TABLE IF EXISTS pnl_total;

CREATE TABLE pnl_total(
    id INTEGER PRIMARY KEY,
    id_wallet INTEGER REFERENCES wallet (id),
    asset TEXT,
    value NUMERIC,
    currency TEXT
);

CREATE INDEX pnl_total_id_index ON pnl_total (id ASC);


--sqlite3
--.open moon.db
--.read ./src/conf/db.sql
--.tables