FROM nginx:latest

# move config
RUN rm /etc/nginx/nginx.conf
COPY ./nginx /etc/nginx


ARG DEV
RUN if [ "$DEV" = "TRUE" ]; then \
    # If not DEV then copy all static files into the container
    COPY ./sensor_portal_docs /sensor_portal_docs \
fi

# enable sites
RUN mv /etc/nginx/sites-available /etc/nginx/sites-enabled/