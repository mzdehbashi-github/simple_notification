#!/bin/bash

# Number of concurrent POST requests
num_post_requests=100

# POST endpoint URL
post_endpoint="http://localhost:8000/notifications"

# Function to send a POST request to create a notification
send_post_request() {
  response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"user_id": 1, "text": "Holla amigo"}' $post_endpoint)
  if [ "$response" != "200" ]; then
    echo "Error: POST request failed with status code $response"
  fi
}

# Start sending POST requests concurrently
start_time=$(date +%s)
for ((i = 0; i < num_post_requests; i++)); do
  send_post_request &
done

# Wait for all POST requests to complete
wait


end_time=$(date +%s)
total_time=$((end_time - start_time))

echo "Load test completed."
echo "Total time taken: $total_time seconds"
