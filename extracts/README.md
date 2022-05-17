# Extracts

I've run the script a few times to extract the results of all shows for the period 2016-2022. The results are presented in each json file in the following way:

```
{
	'voting_country1': {
		'country1': {
			'jury_ranks': [int],
			'jury_rank': int,
			'televote_rank': int
		},
		'country2': {
			...
		},
		...
	},
	'voting_country2': {
		...
	},
	...
}
```

Note that `jury_rank` is the jury rank as presented on Eurovision.tv (remember the calculation for the overall jury rank [changed in 2018](https://web.archive.org/web/20191212163612/https://eurovision.tv/story/subtle-significant-ebu-changes-weight-individual-jury-rankings)), while `jury_ranks` are the individual jury rankings of the country.