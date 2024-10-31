import duckdb

# Connect to your DuckDB database
conn = duckdb.connect('C:\\Users\\filip\\Desktop\\CS2_Scraping_Project\\duckdb\\cs2.duckdb')

# Create tables from Parquet files

#conn.execute("CREATE TABLE matches AS SELECT * FROM 'C:\\Users\\filip\\Desktop\\CS2_Scraping_Project\\matches\\matches.parquet';")
#conn.execute("CREATE TABLE events AS SELECT * FROM 'C:\\Users\\filip\\Desktop\\CS2_Scraping_Project\\events\\events.parquet';")
#conn.execute("CREATE TABLE players AS SELECT * FROM 'C:\\Users\\filip\\Desktop\\CS2_Scraping_Project\\players\\players.parquet';")

# Delete all data but keep the structure
conn.execute("DELETE FROM matches;")
conn.execute("DELETE FROM events;")
conn.execute("DELETE FROM players;")


# Close the connection
conn.close()
