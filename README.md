# Algo Trading

## Purpose
The purpose of this repository is three-fold:
* Keep my skills sharp
* Learn more about
  * SQL
  * Unit testing
  * Python data visualization frameworks
* Make investing less stressful

As I work I intend replace scripts with well-structured, class-organized code that
I can use in my day to day life easily.  With enough time it will hopefully be automated.

## Workflow
Going forward, I plan to use separate branches to add features/functions/scripts
to this repo.  After development and testing they will be added to the main branch
using a rebase.

## Data
This code relies on a sqlite database to store and retrieve information.  The schema of
that database is recorded below:

CREATE TABLE IF NOT EXISTS "Securities" (SecurityID INTEGER PRIMARY KEY, SecurityTicker TEXT NOT NULL, SecurityName TEXT, SharesOwned, UNIQUE (SecurityTicker));

CREATE TABLE IF NOT EXISTS "History" (SecurityID INTEGER NOT NULL, Datetime TEXT NOT NULL, Open REAL NOT NULL, High REAL NOT NULL, Low REAL NOT NULL, Close REAL NOT NULL, Volume INTEGER NOT NULL, OpenInt REAL NOT NULL, FOREIGN KEY (SecurityID) REFERENCES Securities (SecurityID), PRIMARY KEY(SecurityID, Datetime));
