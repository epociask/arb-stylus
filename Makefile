fetch_data:
	curl -L https://static.crates.io/db-dump.tar.gz > dump.tar.gz
	mv dump.tar.gz ./.data/dump.tar.gz
	cd .data && tar -xzf dump.tar.gz
	rm ./.data/dump.tar.gz