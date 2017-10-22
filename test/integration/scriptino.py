from .../lodegML import system as sss

system = sss.LodegSystem(ml_autorun = False)

system.executeCompleteExtraction()

system.export_data(export_type='json', pretty_printing = True, course = 'course1', user = 'user1', selected_keys = ['notes_per_type','number_of_notes'])
