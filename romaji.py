import json

romaji_dict = {}

with open("romaji.json", "r") as f:
    romaji_dict = json.load(f)


class TypingQuestion:
    table: list[list[list[str]]]
    i = 0
    inputting = ""
    inputted = ""
    question = ""
    n_mode = False

    def __init__(self, question: str):
        self.question = question
        self.table = []
        for i in range(len(question)):
            row = []
            for j in range(1, 5):
                substr = question[i : i + j]
                if substr in romaji_dict:
                    if substr == "ん":
                        # 次の文字があいうえお、なにぬねの、やゆよ、んの場合はnnまたはxn、そうでない場合はnも追加
                        next_char = question[i + j : i + j + 1]
                        n_list = ["nn", "xn"]
                        if next_char not in [
                            "あ",
                            "い",
                            "う",
                            "え",
                            "お",
                            "や",
                            "ゆ",
                            "よ",
                            "ん",
                        ]:
                            n_list.insert(0, "n")
                        row.append(tuple(n_list))
                    else:
                        row.append(romaji_dict[substr])
                else:
                    row.append(tuple())
            self.table.append(row)

    def validate(self, keys: str):
        for j, row in enumerate(self.table[self.i]):
            if keys in row:
                self.i += j + 1
                return True
        return False

    @property
    def is_completed(self):
        return self.i == len(self.table)

    def press(self, key: str):
        if len(key) > 1:
            raise ValueError("key must be a single character")
        if self.n_mode:
            self.n_mode = False
            self.i += 1
            self.inputting = ""
            if key == "n":
                self.inputted += "n"
                return True
        for j, tokens in enumerate(self.table[self.i]):
            for token in tokens:
                if token.startswith(self.inputting + key):
                    self.inputting += key
                    self.inputted += key
                    if token == self.inputting:
                        if token == "n":
                            self.n_mode = True
                            return True
                        self.i += j + 1
                        self.inputting = ""
                    return True
        return False

    @property
    def completed_chars(self):
        return self.question[: self.i]

    @property
    def remaining_chars(self):
        return self.question[self.i :]

    def romanize_remaining(self):
        # 最初の文字（現在入力中のもの）だけは特別な処理をする
        patterns = self.allowed_patterns()
        if not patterns:
            return ""
        current = patterns[0]
        yield current[1].replace(self.inputting, "", 1)
        if current[1] == "n":
            yield "n"
        for char in self.remaining_chars[current[0] :]:
            yield tuple(romaji_dict.get(char, tuple()))[0]

    def allowed_patterns(self, key: str = ""):
        patterns = []
        if self.is_completed:
            return []
        for j, row in enumerate(self.table[self.i]):
            for pattern in row:
                if pattern.startswith(self.inputting + key):
                    patterns.append((j + 1, pattern))
        return patterns
