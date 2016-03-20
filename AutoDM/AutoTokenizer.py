class Tokenizer(object):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        try:
            self.next = next(self.tokenizer)
        except Exception as e:
            self.next = None
    def consume(self):
        temp = self.next
        try:
            self.next = next(self.tokenizer)
        except Exception as e:
            self.next = None
        return temp
    def peek(self):
        return self.next
    def hasNext(self):
        return self.next is not None


class FileTokenizer(Tokenizer):
    def __init__(self,filename):
        tok = tokenizeFile(filename)
        Tokenizer.__init__(self,tok)


class TextTokenizer(Tokenizer):
    def __init__(self,s):
        tok = tokenizeString(s)
        Tokenizer.__init__(self,tok)


valid_id = "abcdefghijklmnopqrstuvwxyz1234567890_"

def tokenizeFile(filename):
    '''
    Tokenizes file into ids, quotes and non-word characters
    :param filename: file to tokenize
    :return: generator
    '''
    with open(filename, "r") as f:
        in_quotes = False
        acc = ""
        for line in f:
            for c in line:
                if c != "\"" and in_quotes:
                    acc += c
                elif c=="\"":
                    if in_quotes:
                        in_quotes = False
                    else:
                        in_quotes = True
                    if len(acc)>0:
                        yield acc
                        acc = ""
                elif c=="#":
                    break
                elif c.isspace():
                    if len(acc)>0:
                        yield acc
                        acc = ""
                elif c.lower() not in valid_id:
                    if len(acc)>0:
                        yield acc
                        acc = ""
                    yield c
                else:
                    acc += c
            if len(acc)>0:
                yield acc
                acc = ""


def tokenizeString(line):
    '''
    Tokenizes string into ids, quotes, and non-word characters
    :param line: string to tokenize
    :return: generator
    '''
    in_quotes = False
    acc = ""
    for c in line:
        if c != "\"" and in_quotes:
            acc += c
        elif c=="\"":
            if in_quotes:
                in_quotes = False
            else:
                in_quotes = True
            if len(acc)>0:
                yield acc
                acc = ""
        elif c=="#":
            break
        elif c.isspace():
            if len(acc)>0:
                yield acc
                acc = ""
        elif c.lower() not in valid_id:
            if len(acc)>0:
                yield acc
                acc = ""
            yield c
        else:
            acc += c
    if len(acc)>0:
        yield acc
