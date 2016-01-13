''' Opens a file representing known (or queued to learn) words and a file containing arbitrary words. Produces a file with words to be learned.
    Intended usage is to gen known words by exporting them from Anki, get questioned words from a text (scanned book page, a page from Internet etc.)
    and get as a result list of words which are unknown at the moment a should be queued for learning.

    Output file is by default intentionally in random order.
    Each word found is presented on one line.
    If a questioned word is not in its basic state (infinitive for verbs, singular for nouns etc.) then word with its
    basic state in parenthesis is present)
    If can't determine if a word is in a basic state (e.g. books = many exemplars of a book or a financial record), the script chooses that word is not
    in it's basic state ( books => "books (book)")
    If even a word in basic state is not "known" than both forms (found and basic) are presented in the output (books => "book" + "books (book)"
    E.g.
    book
    look
    looks (look)
    looking (look)


'''