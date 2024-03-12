The repository is built using a DevContainer in VS code.  This automatically installs all required tech (python, poetry, python libraries), and builds the environment for you to work inside of a container. No more issues of 'it works on my machine' to be found here. The file paths may end up weird, but I believe it should all work out of the container. 

# Approach
There are a few options we could take to ingest data. In my current work, I use Pandas (now Polars) for this kind of small csv ingestion work,
but since we will be doing some analysis and joins (and the Pandas API for this is obtuse), instead of juggling python > pandas > Datbase > SQL
I am going to use DuckDB to build an in-memory database for analysis.

The SQL is easy, once the data is in a usable condition

# Matching
My initial instinct for matching the schools to the attendance values was to use the Levenshtein Distance to do some fuzzy matching between the datasets. While it worked for the most part, there were a few schools it seemed to have trouble matching, which I felt were pretty obvious (Alabama-Heersink in particular).

If I were to spend more time on this, other approaches I may look at would include:
- Using an LLM to match between the lists
- Building something to find the 'uniqueness' of a word, and matching the most unique schools first, and then performing fuzzy matching on the rest (i.e. Heersink is a unique word, and would only have one match compared to something like 'University')

As with all DE work, there was some odd instances of messy data within the Univiersities.csv provided. Many 'State' fields were incorrect (Arkansas schools listed with an Alaska state code, WA schools listed as Western Austraila as the state within the US). On the small dataset, cleaning it manually is an option I could have pursued as my approach required an accurate state code to match universities, but for an interview task, I continued with the assumption that all of the provided data was accurate.


# SQL Query Notes
 - This doesn't match all schools, as we are only considering 'higher matched' confidence intervals. If we were certain that all the schools were properly matched (perhaps by hand), then we coulld exclude the clause which filters by confidence interval. Lower matched ones weren't always accurate, so I felt it best to have a cutoff of what we consider 'good enough' for this preliminary discovery process
 - We are specifically only looking at the latest semester (students with a term start after 2023-08-01) since the ask was to look at the current rate and not rate over time in the past. The ask seemed to emphasize the solution for determining user subscription status, so perhaps this was too simplistic of a choice at how I went ahead with my analysis.
 - Some Penetration rates are higher than 1. This would lead me to consider that the schools were matched improperly, but the two that have a >1 penetration rate are both matched correctly. This could mean students are lying about the school they are attending, or that the data we have is inaccurate from either dataset we used to build the report