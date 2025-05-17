# api_learning



- use case:
 - hackathon certificate 
 - course completion
 - payment slip
 - offer letter
 - hackathon chiefguest certificate
 - internship certificate
 - fees receipt
 - 


- users:
    - admin
        - generate certificate in bulk
        - generate certificate for single user
        - modify certificate
    - user
        - view generated certificate,
        - download certificate

- routes
    - admin
        - /admin/generate_certificate_in_bulk
        - /admin/generate_certificate_for_single_user
        - /admin/modify_certificate/{certificate_id}
    - user
        - /user/view_generated_certificate
        - /user/download_certificate
        - /user/register
    - common
        - /login
        - forgot password
        - reset password
        - logout