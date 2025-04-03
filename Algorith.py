from sklearn.neighbors import KNeighborsClassifier

# Initialize classifier and data storage
knn = KNeighborsClassifier(n_neighbors=1)  # You can adjust neighbors later
training_data = []  # Stores (command, response) pairs
labels = []  # Stores corresponding labels for classification

def update_learning_data(command, response):
    training_data.append(get_vector(command))  # Convert command to vector
    labels.append(response)

def learn_from_data():
    if len(training_data) > 0:
        knn.fit(np.array(training_data), labels)

def get_basic_ai_response(command):
    # Get nearest response based on user input
    if len(training_data) > 0:
        command_vector = get_vector(command)
        prediction = knn.predict([command_vector])[0]
        return prediction
    else:
        return "I'm still learning. Could you help me out?"

