--  Initializer for the diversaspot database table. DO NOT RUN.
--  ran with `cat dbinit.sql | cockroach sql --url $DATABASE_URL`
--  ^^ NOTE: scheme must be postgresql for the DATABASE_URL
CREATE TABLE diversaspots (
    timestamp VARCHAR PRIMARY KEY,
    spotter VARCHAR,
    tagged TEXT[],
    image_url VARCHAR,
    flagged BOOLEAN,
    semester VARCHAR NULL,
);