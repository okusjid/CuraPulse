# # from yourapp.models import CustomUser  # Replace 'yourapp' with your actual app name
#
# CustomUser.objects.create_user(
#     username='john_doe',
#     password='john1234',
#     role='doctor',
#     full_name='John Doe',
#     email='john.doe@example.com',
#     phone_number='1234567890',
#     specialization='Cardiology',
#     gender='male'
# )
#
# CustomUser.objects.create_user(
#     username='jane_smith',
#     password='jane1234',
#     role='doctor',
#     full_name='Jane Smith',
#     email='jane.smith@example.com',
#     phone_number='0987654321',
#     specialization='Pediatrics',
#     gender='female'
# )
#
# CustomUser.objects.create_user(
#     username='michael_brown',
#     password='michael1234',
#     role='doctor',
#     full_name='Michael Brown',
#     email='michael.brown@example.com',
#     phone_number='5556667777',
#     specialization='Neurology',
#     gender='male'
# )
#
# CustomUser.objects.create_user(
#     username='emma_white',
#     password='emma1234',
#     role='doctor',
#     full_name='Emma White',
#     email='emma.white@example.com',
#     phone_number='4445556666',
#     specialization='Dermatology',
#     gender='female'
# )
#
# CustomUser.objects.create_user(
#     username='robert_jones',
#     password='robert1234',
#     role='doctor',
#     full_name='Robert Jones',
#     email='robert.jones@example.com',
#     phone_number='7778889999',
#     specialization='Orthopedics',
#     gender='male'
# )
#
# from yourapp.models import Patient  # Replace 'yourapp' with your actual app name
# from datetime import date
#
# Patient.objects.create(
#     name='Alice Johnson',
#     email='alice.johnson@example.com',
#     phone_number='1234567890',
#     date_of_birth=date(1985, 7, 15),
#     gender='female'
# )
#
# Patient.objects.create(
#     name='Bob Williams',
#     email='bob.williams@example.com',
#     phone_number='0987654321',
#     date_of_birth=date(1990, 5, 23),
#     gender='male'
# )
#
# Patient.objects.create(
#     name='Carol Davis',
#     email='carol.davis@example.com',
#     phone_number='5556667777',
#     date_of_birth=date(1978, 2, 14),
#     gender='female'
# )
#
# Patient.objects.create(
#     name='David Miller',
#     email='david.miller@example.com',
#     phone_number='4445556666',
#     date_of_birth=date(1992, 11, 30),
#     gender='male'
# )
#
# Patient.objects.create(
#     name='Eve Wilson',
#     email='eve.wilson@example.com',
#     phone_number='7778889999',
#     date_of_birth=date(1983, 3, 7),
#     gender='female'
# )
#
#
# appointments = [
#     Appointment.objects.create(doctor=doctor1, patient=patient1, scheduled_at=now + timedelta(days=1, hours=9)),
#     Appointment.objects.create(doctor=doctor1, patient=patient2, scheduled_at=now + timedelta(days=2, hours=10)),
#     Appointment.objects.create(doctor=doctor2, patient=patient3, scheduled_at=now + timedelta(days=3, hours=11)),
#     Appointment.objects.create(doctor=doctor2, patient=patient4, scheduled_at=now + timedelta(days=4, hours=14)),
#     Appointment.objects.create(doctor=doctor3, patient=patient5, scheduled_at=now + timedelta(days=5, hours=15)),
#     Appointment.objects.create(doctor=doctor3, patient=patient6, scheduled_at=now + timedelta(days=6, hours=16)),
#     Appointment.objects.create(doctor=doctor4, patient=patient7, scheduled_at=now + timedelta(days=7, hours=17)),
# ]