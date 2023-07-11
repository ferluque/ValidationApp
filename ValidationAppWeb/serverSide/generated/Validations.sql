CREATE TABLE Images (
	filename VARCHAR(255),	-- added default type
	PRIMARY KEY (filename)
);
CREATE TABLE Users (
	username VARCHAR(255),	-- added default type
	password VARCHAR(255),	-- added default type
	active VARCHAR(255),	-- added default type
	admin VARCHAR(255),	-- added default type
	consensus VARCHAR(255),	-- added default type
	PRIMARY KEY (username)
);
CREATE TABLE Models (
	name VARCHAR(255),	-- added default type
	PRIMARY KEY (name)
);
CREATE TABLE Validation (
	filename2 VARCHAR(255),	-- renamed from: filename; added default type
	username2 VARCHAR(255),	-- renamed from: username; added default type
	username VARCHAR(255),	-- added default type
	filename VARCHAR(255),	-- added default type
	level1 VARCHAR(255),	-- added default type
	level2 VARCHAR(255),	-- added default type
	timestamp VARCHAR(255),	-- added default type
	ignored VARCHAR(255),	-- added default type
	PRIMARY KEY (filename2, username2),
	FOREIGN KEY (filename2) REFERENCES Images (filename) ON DELETE CASCADE,
	FOREIGN KEY (username2) REFERENCES Users (username) ON DELETE CASCADE
);
