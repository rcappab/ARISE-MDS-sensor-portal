FROM nginx:latest

# move config
RUN rm /etc/nginx/nginx.conf
COPY ./nginx /etc/nginx

COPY ./sensor_portal_docs /sensor_portal_docs
COPY ./sensor_portal/static /backend_static




# enable sites
RUN mv /etc/nginx/sites-available /etc/nginx/sites-enabled/