import duckdb
import pandas as pd
from med_school_matching import match_schools


SOURCE_FOLDER = "/workspaces/python3-poetry-pyenv/data_sources/"
DATA_SOURCES = {
    "users": "users.csv",
    "universities": "universities.csv",
    "subscriptions": "subscriptions.csv",
}
ENROLLMENT_DATA = pd.read_excel(
    "/workspaces/python3-poetry-pyenv/data_sources/enrollment.xlsx"
)
UNIVERSITIES_DATA = pd.read_csv(
    "/workspaces/python3-poetry-pyenv/data_sources/universities.csv"
)


def main() -> None:
    conn = duckdb.connect(database=":memory:", read_only=False)
    populate_database(conn)
    
    # See SQL Query Notes on the readme.md
    conn.sql(
        """
        select 
          uni.name,
          round(count(distinct u.id)/sm.student_count,2) as penetration_rate
        from users u
          join universities uni on u.university_id=uni.id
          join school_matching sm on sm.university_id=uni.id
          join subscriptions sub on u.id=sub.user_id
        where 
          sm.confidence >= 70 
          and sub.transaction_type='PAID'
          and sub.term_start > '2023-08-01'
        group by 
          uni.name, sm.student_count
        order by 
          penetration_rate desc
        
    """
    ).show()


def populate_database(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Fills the in-memory database with data from the csvs and source enrollment dataset
    """
    df = match_schools(UNIVERSITIES_DATA, ENROLLMENT_DATA)
    conn.sql(
        """
        Create table school_matching as
        select *
        from df
    """
    )
    for table in DATA_SOURCES:
        csv_data = conn.read_csv(f"{SOURCE_FOLDER}/{DATA_SOURCES[table]}")
        conn.sql(
            f"""
            CREATE TABLE {table} AS
            SELECT *
            FROM csv_data
        """
        )


def db_exploration(conn: duckdb.DuckDBPyConnection):
    
    conn.sql(
        """
        SELECT u.name, u.program_year, uni.name as university_name
        FROM users u
        join universities uni on u.university_id=uni.id
        order by university_name asc
    """
    ).show()
    print()
    conn.sql(
        """
        SELECT state, count(state)
        FROM universities
        where country='United States of America' and state!='NULL'
        group by state
        order by state asc
    """
    ).show()
    conn.sql(
        """
        SELECT *
        FROM universities
        where state='AK'
    """
    ).show()

    conn.sql(
    """
        SELECT uni.state, count(*)
        FROM users u
        join universities uni on u.university_id=uni.id
        join subscriptions sub on u.id=sub.user_id
        where 
            sub.transaction_type='PAID' 
            and lower(uni.country)='united states of america'
            and uni.country!='NULL'
            and uni.state !='NULL'
        group by uni.state
        order by uni.state asc
    """
    ).show()



if __name__ == "__main__":
    main()
