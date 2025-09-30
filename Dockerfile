# Use Docker Hub / GHCR image
FROM ghcr.io/jiotv-go/jiotv_go:latest

# Set environment variables
ENV TZ=Asia/Kolkata
ENV JIOTV_PATH_PREFIX=/app/.jiotv_go
ENV JIOTV_DRM=true

# Expose port 5001
EXPOSE 5001

# Start the server
CMD ["jiotv_go", "serve", "--port", "5001"]
