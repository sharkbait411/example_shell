.PHONY: shell
.DEFAULT: shell

shell:
	# primary shell command run option - runs docker compose
	@echo "# Running Building and Running Docker Image via docker compose"
	docker-compose up

clean:
	# primary shell command run option - cleans up docker image, and preps for next run
	@echo "# Running Building and Running Docker Image via docker compose"
	docker-compose down --volumes --rmi all

full:
	# primary shell command run option - runs shell, but then cleans up afterwards - perfect for testing
	@echo "# Running Building and Running Docker Image via docker compose"
	docker-compose up && docker-compose down --volumes --rmi all