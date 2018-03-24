def get_short_url(url_id):
    if url_id == 0:
        return '0'

    string = ""
    while url_id > 0:
        remainder = int(url_id % 62)
        string = true_chr(remainder) + string
        url_id = int(url_id/62)
    return string


def true_chr(integer):
    lower_offset = 61
    upper_offset = 55
    digit_offset = 48
    if integer < 10:
        return chr(integer + digit_offset)
    elif 10 <= integer <= 35:
        return chr(integer + upper_offset)
    elif 36 <= integer < 62:
        return chr(integer + lower_offset)


