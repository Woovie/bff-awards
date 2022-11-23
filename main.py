import requests, json, pdb

from itertools import chain

import bs4

class Nominator:
    def __init__(self, voter: dict):
        print(voter["id"])
        self.voter = voter
        self.nominations = []
        self.retrieve_vote()

    def __json__(self):
        return {
            "voter": self.voter,
            "nominations": [x.__json__() for x in self.nominations]
        }

    def retrieve_vote(self):
        req = requests.get(self.voter["url"])
        self._process_votes_(req.text)

    def _process_votes_(self, html: str):
        votes = bs4.BeautifulSoup(html, "html.parser").find(class_="nomination_rows").find_all(class_="nomination_row")
        for vote in votes:
            self._process_vote_(vote)

    def _process_vote_(self, vote: bs4.BeautifulSoup):
        bad_url = "https://store.steampowered.com/app/2218020/Steam_Awards_Skip_Category_Best_Game_On_The_Go/"
        base = vote.find(class_="younominated_game")
        game_url = "N/a"
        game_name = "N/a"
        category_name = vote.find(class_="category_title").find_all('div')[-1].text
        if base:
            if base.attrs["href"] != bad_url:
                game_url = base.attrs["href"]
                game_name = base.img.attrs["title"]
        nomination = Nomination(game_url, game_name, category_name)
        self.nominations.append(nomination)

class Nomination:
    def __init__(self, url: str, name: str, category: str):
        self.url = url
        self.name = name
        self.category = category
    
    def __json__(self) -> dict:
        return {
            "url": self.url,
            "name": self.name,
            "category": self.category
        }

class Categories:
    def __init__(self):
        with open("categories.json", "r") as catdata:
            self.categories = json.load(catdata)

class Voters:
    def __init__(self):
        with open("voters.json", "r") as voterdata:
            self.voters = json.load(voterdata)

class ProcessVotes:
    def __init__(self):
        self.categories = Categories().categories
        self.voters = Voters().voters
        self.nominators = []
        self.start()

    def start(self):
        for voter in self.voters:
            self.nominators.append(Nominator(voter))
        writeable = [x.__json__() for x in self.nominators]
        with open("results.json", "w") as writer:
            json.dump(writeable, writer)
        final_string = f"ID|Vote URL|{'|'.join(list(chain.from_iterable((x.rsplit(' ', 1)[0], 'URL') for x in self.categories)))}\n"
        for voter in writeable:
            final_string += f"{voter['voter']['id']}|{voter['voter']['url']}|{'|'.join(list(chain.from_iterable((x['name'], x['url']) for x in voter['nominations'])))}\n"
        with open("results.csv", "w") as writer:
            writer.write(final_string)
            writer.close()
        

if __name__ == "__main__":
    ProcessVotes()