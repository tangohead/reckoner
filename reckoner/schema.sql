BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(50) NOT NULL,
	"email"	VARCHAR(100) NOT NULL,
	"password"	VARCHAR NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "reckon" (
	"id"	INTEGER NOT NULL,
	"question"	VARCHAR(240) NOT NULL,
	"creation_date"	DATETIME NOT NULL,
	"edit_date"	DATETIME NOT NULL,
	"end_date"	DATETIME NOT NULL,
	"creator_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("creator_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "reckon_option" (
	"id"	INTEGER NOT NULL,
	"option"	VARCHAR(240) NOT NULL,
	"reckon_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("reckon_id") REFERENCES "reckon"("id")
);
CREATE TABLE IF NOT EXISTS "reckon_response" (
	"id"	INTEGER NOT NULL,
	"reckon_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"reckon_option_id"	INTEGER NOT NULL,
	"probability"	FLOAT NOT NULL,
	"response_date"	DATETIME NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	FOREIGN KEY("reckon_id") REFERENCES "reckon"("id"),
	FOREIGN KEY("reckon_option_id") REFERENCES "reckon_option"("id")
);
COMMIT;
