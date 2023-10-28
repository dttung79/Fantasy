from extract_file import extract_data


if __name__ == "__main__":
    url = "https://www.livefpl.net/leagues/1349328"
    

    team_names = ['savapain', 'PhiHung50', 'Nani29', 'Onion XXL']
    data = extract_data(url, team_names)
    for row in data:
        print(row)
