# NLP tools
from nltk.sentiment import vader
from transformers import pipeline


# non ML approach, rule based
def vader_sentiment_analysis(comments):
    """
    Function to analyze sentiment of comments using Vader Sentiment Analysis.
    Uses a bag of words approach to determine sentiment of comments. Removes stop words and Calculates a score for each work in the comment and then averages the scores to get a sentiment score for the comment.

    NOTE: Vader Sentiment Analysis has it's flaws, does not account for relationships between words in a sentence.

    Args:
        comments (list): list of comments to analyze

    Returns:
        sentiment_scores (list): list of sentiment scores for each comment from -1 to 1
    """

    analyzer = vader.SentimentIntensityAnalyzer()

    sentiment_scores = []

    for comment in comments:
        sentiment = analyzer.polarity_scores(comment)

        # append the compound score to the sentiment_scores list
        sentiment_scores.append(sentiment["compound"])

    return sentiment_scores


# ML approach, transformer model
def huggingface_sentiment_analysis(comments):
    """
    Function to analyze sentiment of comments using HuggingFace Sentiment Analysis.
    Uses a transformer model to determine sentiment of comments.

    Args:
        comments (list): list of comments to analyze

    Returns:
        sentiment_scores (list): list of sentiment scores for each comment from -1 to 1
    """

    # can specify model,tokenizer for the pipeline to use
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    sentiment_scores = []

    for comment in comments:
        # Tokenize the comment and check the length of the tokenized input
        tokenized_comment = sentiment_pipeline.tokenizer.tokenize(comment)

        if len(tokenized_comment) < 510:
            # Truncate the tokenized input to the first 512 tokens
            tokenized_comment = tokenized_comment[:510]

            # Convert the truncated tokenized input back to text
            truncated_comment = sentiment_pipeline.tokenizer.convert_tokens_to_string(
                tokenized_comment
            )

            # Perform sentiment analysis on the truncated comment
            sentiment = sentiment_pipeline(truncated_comment)
            sentiment_scores.append(sentiment)

    # change sentiment score to be a value between -1 and 1, remove label
    sentiment_scores = [
        (
            sentiment[0]["score"]
            if sentiment[0]["label"] == "POSITIVE"
            else -sentiment[0]["score"]
        )
        for sentiment in sentiment_scores
    ]

    return sentiment_scores


def comments_sentiment_analysis(comments, method="vader"):
    """
    Function to analyze sentiment of comments using specified method. Takes average of sentiment scores for each comment in a year-month pair.

    Args:
        comments (list): list of comments to analyze, ordered by year-month pairs
        method (str): method to use for sentiment analysis, either "vader" or "ml"

    Returns:
        results (dict): dictionary containing sentiment analysis results for each year-month pair:
        {
            "year-month": {
                "avg_sentiment": float,
                "max_sentiment_comment": str,
                "max_sentiment": float,
                "min_sentiment_comment": str,
                "min_sentiment": float,
            },
            ...
        }
    """

    results = {}

    if method == "vader":
        for key, value in comments.items():
            # check if no comments for the year-month pair
            if not value:
                continue

            # value contains an array of comments for the year-month pair
            sentiment_scores = vader_sentiment_analysis(value)

            # average sentiment score for the year-month pair
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

            # find the comment text with the highest sentiment
            max_sentiment_score = max(sentiment_scores)
            max_sentiment_comment = value[sentiment_scores.index(max_sentiment_score)]

            # find the comment with the lowest sentiment
            min_sentiment_score = min(sentiment_scores)
            min_sentiment_comment = value[sentiment_scores.index(min_sentiment_score)]

            results[key] = {
                "avg_sentiment": avg_sentiment,
                "max_sentiment_comment": max_sentiment_comment,
                "max_sentiment": max_sentiment_score,
                "min_sentiment_comment": min_sentiment_comment,
                "min_sentiment": min_sentiment_score,
            }

    elif method == "ml":
        for key, value in comments.items():
            # check if no comments for the year-month pair
            if not value:
                continue

            sentiment_scores = huggingface_sentiment_analysis(value)

            # average sentiment score for the year-month pair
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

            # find the comment text with the highest sentiment
            max_sentiment_score = max(sentiment_scores)
            max_sentiment_comment = value[sentiment_scores.index(max_sentiment_score)]

            # find the comment with the lowest sentiment
            min_sentiment_score = min(sentiment_scores)
            min_sentiment_comment = value[sentiment_scores.index(min_sentiment_score)]

            results[key] = {
                "avg_sentiment": avg_sentiment,
                "max_sentiment_comment": max_sentiment_comment,
                "max_sentiment": max_sentiment_score,
                "min_sentiment_comment": min_sentiment_comment,
                "min_sentiment": min_sentiment_score,
            }

    # order the results by year-month pairs
    results = dict(sorted(results.items(), key=lambda x: x[0]))

    return results