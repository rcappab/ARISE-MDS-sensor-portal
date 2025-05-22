FROM nginx:latest

# move config
RUN rm /etc/nginx/nginx.conf
COPY ./nginx /etc/nginx


ARG DEV
RUN if [ "$DEV" = "TRUE" ]; then \
    COPY /sensor_portal_docs_source /sensor_portal_docs; \
    COPY /sensor_portal/static /backend_static; \
fi


# enable sites
RUN mv /etc/nginx/sites-available /etc/nginx/sites-enabled/