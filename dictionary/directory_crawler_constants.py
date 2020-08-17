_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"

directory_url = "https://www.exrx.net/Lists/Directory"
type_a = 'WeightExercises/'
type_b = 'Stretches/'
type_a_search = 'WeightExercises/(.*)/'
type_b_search = 'Stretches/(.*)/'

neck = {"name": "Neck",
        "muscles": ["Sternocleidomastoid", "Splenius"],
        "url": "https://www.exrx.net/Lists/ExList/NeckWt"}
shoulders = {"name": "Shoulders",
             "muscles": ["DeltoidAnterior",
                         "DeltoidLateral", "DeltoidPosterior", "Supraspinatus"],
             "url": "https://www.exrx.net/Lists/ExList/ShouldWt"}
upperarms = {"name": "UpperArms",
             "muscles": ["Triceps", "Biceps", "Brachialis"],
             "url": "https://www.exrx.net/Lists/ExList/ArmWt"}
forearms = {"name": "Forearms",
            "muscles": ["Brachioradialis", "WristFlexors",
                        "WristExtensors", "Pronators", "Supinators"],
            "url": "https://www.exrx.net/Lists/ExList/ForeArmWt"}
back = {"name": "Back",
        "muscles": ["BackGeneral", "LatissimusDorsi", "TrapeziusUpper",
                    "Rhomboids", "Infraspinatus", "Subscapularis"],
        "url": "https://www.exrx.net/Lists/ExList/BackWt"}
chest = {"name": "Chest",
         "muscles": ["PectoralSternal", "PectoralClavicular",
                     "PectoralisMinor", "SerratusAnterior"],
         "url": "https://www.exrx.net/Lists/ExList/ChestWt"}
waist = {"name": "Waist",
         "muscles": ["RectusAbdominis", "Obliques", "ErectorSpinae"],
         "url": "https://www.exrx.net/Lists/ExList/WaistWt"}
hips = {"name": "Hips",
        "muscles": ["GluteusMaximus", "HipAbductors",
                    "HipFlexors", "HipExternalRotators"],
        "url": "https://www.exrx.net/Lists/ExList/HipsWt"}
thighs = {"name": "Thighs",
          "muscles": ["Quadriceps", "Hamstrings", "HipAdductors"],
          "url": "https://www.exrx.net/Lists/ExList/ThighWt"}
calves = {"name": "Calves",
          "muscles": ["Gastrocnemius", "Soleus", "TibialisAnterior"],
          "url": "https://www.exrx.net/Lists/ExList/CalfWt"}

muscle_groups = [neck, shoulders, upperarms, forearms,
                 back, chest, waist, hips, thighs, calves]
