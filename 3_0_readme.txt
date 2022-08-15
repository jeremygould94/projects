Readme for Sentiment analysis

Steps:
> Download feedback in csv and remove "3_" prefix from name.
> Populate with new feedback or keep existing
> Run customer feedback script.
> Feedback topics are manually selected and flagged through key words, e.g. "staff" indicates "service".
> Import feedback output into PowerBI etc to present.

How it works:
> We use vadersentiment module to gauge sentiment but this works on the feedback as a whole.
> If we have feedback like, "the food was good but the staff were rude",
  then we need to split this into "the food was good" and "the staff were rude",
  so we can give a good score to the "food" topic and a bad score to the "service" topic.
> So we do this first then apply vader to the sections, also looking for keywords that identify each topic.
> This gives us scoring for eaction section of the feedback.
