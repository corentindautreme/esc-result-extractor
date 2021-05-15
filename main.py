from requests_html import HTMLSession
import json
import re

points = [0, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1]
ranks = [0, 10, 9, 8, 7, 6, 5, 4, 3, 0, 2, 0, 1]

BASE_URL = 'https://eurovision.tv/event/{}/{}/results'

session = HTMLSession()

result_links = [
	BASE_URL.format('tel-aviv-2019', 'first-semi-final'),
	BASE_URL.format('tel-aviv-2019', 'second-semi-final'),
	BASE_URL.format('tel-aviv-2019', 'grand-final'),
	BASE_URL.format('lisbon-2018', 'first-semi-final'),
	BASE_URL.format('lisbon-2018', 'second-semi-final'),
	BASE_URL.format('lisbon-2018', 'grand-final'),
	BASE_URL.format('kyiv-2017', 'first-semi-final'),
	BASE_URL.format('kyiv-2017', 'second-semi-final'),
	BASE_URL.format('kyiv-2017', 'grand-final'),
	BASE_URL.format('stockholm-2016', 'first-semi-final'),
	BASE_URL.format('stockholm-2016', 'second-semi-final'),
	BASE_URL.format('stockholm-2016', 'grand-final')
]

for result_link in result_links:
	response = session.get(result_link)
	country_votings_links = list(map(lambda e: e.attrs['value'], list(filter(lambda e: 'value' in e.attrs.keys(), response.html.find('.form-select option')))))
	votes_by_country = {}

	for link in country_votings_links:
		voting_country = link[link.rfind('/')+1:]

		# normalizing references to MKD
		if (voting_country == "fyr-macedonia"):
			voting_country = "north-macedonia"

		voting_country_results = {}
		voting_page_response = session.get(link)
		result_lines = voting_page_response.html.find('table.w-full:nth-child(3) tbody tr')

		if len(result_lines) == 0:
			# no detailed table available for this voting country, most likely because their jury vote was invalidated
			# fallback is the previous tables (under "how <country> has voted")
			jury_ranks = []
			televote_points = {}
			jury_points = {}
			# Televote
			televote_lines = voting_page_response.html.find('section.w-full > div:nth-child(4) > div:nth-child(1) > table:nth-child(1) tbody tr')
			for line in televote_lines:
				country = line.find('td:nth-child(2)', first=True).text.strip().lower().replace(' ', '-')
				televote_points[country] = int(line.find('td:nth-child(1)', first=True).text)
			# Jury
			jury_lines = voting_page_response.html.find('section.w-full > div:nth-child(4) > div:nth-child(2) > table:nth-child(1) tbody tr')
			for line in jury_lines:
				country = line.find('td:nth-child(2)', first=True).text.strip().lower().replace(' ', '-')
				jury_points[country] = int(line.find('td:nth-child(1)', first=True).text)

			for country in televote_points.keys():
				results = {
					'jury_ranks': [],
					'jury_rank': ranks[jury_points[country]] if country in jury_points.keys() else 0,
					'televote_rank': ranks[televote_points[country]]
				}
				voting_country_results[country.strip().lower().replace(' ', '-')] = results

			for country in jury_points.keys():
				if country not in televote_points.keys():
					results = {
						'jury_ranks': [],
						'jury_rank': ranks[jury_points[country]],
						'televote_rank': 0
					}
					voting_country_results[country.strip().lower().replace(' ', '-')] = results
		else:
			for line in result_lines:
				country = line.find('td', first=True).text
				jury_ranks = []
				# There can be less than 5 jurors (see Russia in 2016), we need to account for that to hit the right cells of the table
				# jurors_count = voting_page_response.html.find('ul.mb-30', first=True).text.count("Juror")
				jurors_count = voting_page_response.html.find('ul.mb-8', first=True).text.count("Juror")
				for i in range(0,jurors_count):
					jury_ranks.append(int(line.find('td:nth-child(' + str(i+3) +')', first=True).text))
				jury_rank = int(re.sub(r'(?:[0-9]{1,2} point[s]* )*([0-9]{1,2})(st|nd|rd|th)', r'\1', line.find('td:nth-child(' + str(jurors_count+3) + ')', first=True).text))
				televote_rank = int(re.sub(r'(?:[0-9]{1,2} point[s]* )*([0-9]{1,2})(st|nd|rd|th)', r'\1', line.find('td:nth-child(' + str(jurors_count+4) + ')', first=True).text))
				voting_country_results[country.lower().replace(' ', '-')] = {
					'jury_ranks': jury_ranks,
					'jury_rank': jury_rank,
					'televote_rank': televote_rank
				}

		votes_by_country[voting_country] = voting_country_results

	# uncomment the following line to print the results as json
	# print(json.dumps(votes_by_country))

	# recomputing points (2015 style)

	# participating_countries = list(votes_by_country[list(votes_by_country.keys())[0]].keys())
	# participating_countries.append(list(votes_by_country.keys())[0])

	# results = {}
	# for country in participating_countries:
	# 	results[country] = 0

	# for voting_country in votes_by_country.keys():
	# 	votes = votes_by_country[voting_country]
	# 	ranking = []
	# 	for country in votes.keys():
	# 		if len(votes[country]['jury_ranks']) > 0:
	# 			jury_average_rank = sum(votes[country]['jury_ranks']) / len(votes[country]['jury_ranks'])
	# 			average_rank = ( jury_average_rank + votes[country]['televote_rank'] ) / 2
	# 		else:
	# 			average_rank = votes[country]['televote_rank']
	# 		ranking.append({'country': country, 'rank': average_rank, 'televote_rank': votes[country]['televote_rank']})
	# 	ranking = sorted(ranking, key=lambda k: (k['rank'], k['televote_rank']))

	# 	for i, country_rank in enumerate(ranking[:10], start=1):
	# 		results[country_rank['country']] += points[i]

	# print(re.sub(r'https://eurovision\.tv/event/([a-z0-9\-]+)/([a-z\-]+)/results', r'\1\n\2', result_link).replace("-", " ").replace("first semi final", "Semi-final 1").replace("second semi final", "Semi-final 2").title())
	# for country in {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}.keys():
	# 	print(country.replace("-", " ").title() + ";" + str(results[country]))
	# print("\n")
