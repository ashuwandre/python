
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# =====================================================
# STEP 1: GENERATE DUMMY JENKINS DATA
# =====================================================

np.random.seed(42)

applications = {
    "Payment": 0.25,
    "User": 0.08,
    "Notification": 0.18
}

records = []

for app, base_failure_rate in applications.items():

    previous_status = "SUCCESS"
    previous_results = []

    for build in range(1, 41):

        commits = np.random.randint(1, 12)
        changed_files = np.random.randint(1, 25)

        previous_failures = sum(
            result == "FAILURE"
            for result in previous_results[-3:]
        )

        # Generate failure probability
        probability = (
            base_failure_rate
            + (0.12 if previous_status == "FAILURE" else 0)
            + (0.015 * commits)
            + (0.008 * changed_files)
            + (0.06 * previous_failures)
        )

        probability = min(probability, 0.90)

        result = (
            "FAILURE"
            if np.random.random() < probability
            else "SUCCESS"
        )

        records.append({
            "application": app,
            "job_name": app + "_Build",
            "build_number": build,
            "previous_status": previous_status,
            "commits": commits,
            "changed_files": changed_files,
            "previous_failures": previous_failures,
            "result": result
        })

        previous_status = result
        previous_results.append(result)


df = pd.DataFrame(records)

df.to_csv("jenkins_builds.csv", index=False)

print("\n========== DATASET ==========")
print(df.head(10))
print("\nTotal records:", len(df))


# =====================================================
# STEP 2: TRAIN TEST SPLIT
# =====================================================

# Chronological split:
# Builds 1-28 = Training
# Builds 29-40 = Testing

train_df = df[df["build_number"] <= 28].copy()
test_df = df[df["build_number"] > 28].copy()

print("\nTraining records:", len(train_df))
print("Testing records:", len(test_df))


# =====================================================
# STEP 3: MARKOV CHAIN
# =====================================================

states = ["SUCCESS", "FAILURE"]

markov_models = {}

for app in applications:

    app_data = train_df[
        train_df["application"] == app
    ].sort_values("build_number")

    # Count state transitions
    counts = pd.crosstab(
        app_data["previous_status"],
        app_data["result"]
    ).reindex(
        index=states,
        columns=states,
        fill_value=0
    )

    # Laplace smoothing
    probabilities = (
        counts + 1
    ).div(
        counts.sum(axis=1) + 2,
        axis=0
    )

    markov_models[app] = probabilities

    print("\nMarkov Chain:", app)
    print(probabilities.round(3))


# Predict failure probability using Markov Chain

def markov_predict(row):

    app = row["application"]

    current_status = row["previous_status"]

    matrix = markov_models[app]

    return matrix.loc[
        current_status, "FAILURE"
    ]


test_df["markov_failure_probability"] = test_df.apply(
    markov_predict,
    axis=1
)

test_df["markov_prediction"] = np.where(
    test_df["markov_failure_probability"] >= 0.5,
    "FAILURE",
    "SUCCESS"
)


# =====================================================
# STEP 4: RANDOM FOREST MACHINE LEARNING
# =====================================================

# Convert categorical application into numerical columns

encoded_df = pd.get_dummies(
    df,
    columns=["application"],
    dtype=int
)

# Encode previous status
encoded_df["previous_status"] = (
    encoded_df["previous_status"].map({
        "SUCCESS": 0,
        "FAILURE": 1
    })
)

# Encode target
encoded_df["result"] = (
    encoded_df["result"].map({
        "SUCCESS": 0,
        "FAILURE": 1
    })
)

feature_columns = [
    "previous_status",
    "commits",
    "changed_files",
    "previous_failures"
] + [
    col for col in encoded_df.columns
    if col.startswith("application_")
]

X_train = encoded_df.loc[
    train_df.index, feature_columns
]

X_test = encoded_df.loc[
    test_df.index, feature_columns
]

y_train = encoded_df.loc[
    train_df.index, "result"
]

y_test = encoded_df.loc[
    test_df.index, "result"
]


# Train Random Forest

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=4,
    random_state=42,
    class_weight="balanced"
)

rf_model.fit(X_train, y_train)


# Predict failure probability

test_df["ml_failure_probability"] = (
    rf_model.predict_proba(X_test)[:, 1]
)

test_df["ml_prediction"] = np.where(
    test_df["ml_failure_probability"] >= 0.5,
    "FAILURE",
    "SUCCESS"
)


# =====================================================
# STEP 5: HYBRID MODEL
# =====================================================

# Combine Markov and Random Forest probabilities

test_df["hybrid_failure_probability"] = (
    0.5 * test_df["markov_failure_probability"]
    +
    0.5 * test_df["ml_failure_probability"]
)

test_df["hybrid_prediction"] = np.where(
    test_df["hybrid_failure_probability"] >= 0.5,
    "FAILURE",
    "SUCCESS"
)


# Actual results

test_df["actual_result"] = test_df["result"]


# =====================================================
# STEP 6: DISPLAY PREDICTIONS
# =====================================================

print("\n========== PREDICTION RESULTS ==========")

print(test_df[[
    "application",
    "build_number",
    "actual_result",
    "markov_failure_probability",
    "markov_prediction",
    "ml_failure_probability",
    "ml_prediction",
    "hybrid_failure_probability",
    "hybrid_prediction"
]].round(3).to_string(index=False))


# =====================================================
# STEP 7: COMPARE ALL THREE MODELS
# =====================================================

actual = test_df["actual_result"]

predictions = {
    "Markov Chain": test_df["markov_prediction"],
    "Random Forest": test_df["ml_prediction"],
    "Hybrid Model": test_df["hybrid_prediction"]
}

comparison = []

for model_name, prediction in predictions.items():

    comparison.append({
        "Model": model_name,

        "Accuracy": accuracy_score(
            actual, prediction
        ),

        "Precision": precision_score(
            actual,
            prediction,
            pos_label="FAILURE",
            zero_division=0
        ),

        "Recall": recall_score(
            actual,
            prediction,
            pos_label="FAILURE",
            zero_division=0
        ),

        "F1 Score": f1_score(
            actual,
            prediction,
            pos_label="FAILURE",
            zero_division=0
        )
    })


comparison_df = pd.DataFrame(comparison)

print("\n========== MODEL COMPARISON ==========")
print(comparison_df.round(3).to_string(index=False))


# =====================================================
# STEP 8: PREDICT A NEW JENKINS BUILD
# =====================================================

def predict_new_build(
    application,
    previous_status,
    commits,
    changed_files,
    previous_failures
):

    # Markov prediction
    markov_probability = markov_models[
        application
    ].loc[
        previous_status, "FAILURE"
    ]

    # Random Forest input
    new_data = pd.DataFrame([{
        "previous_status": (
            1 if previous_status == "FAILURE" else 0
        ),
        "commits": commits,
        "changed_files": changed_files,
        "previous_failures": previous_failures,
        "application_Notification": (
            1 if application == "Notification" else 0
        ),
        "application_Payment": (
            1 if application == "Payment" else 0
        ),
        "application_User": (
            1 if application == "User" else 0
        )
    }])

    new_data = new_data[feature_columns]

    ml_probability = rf_model.predict_proba(
        new_data
    )[0][1]

    # Hybrid probability
    hybrid_probability = (
        0.5 * markov_probability
        + 0.5 * ml_probability
    )

    print("\n========== NEW BUILD PREDICTION ==========")

    print("Application:", application)
    print("Previous Status:", previous_status)

    print(
        "Markov Failure Probability:",
        round(markov_probability * 100, 2), "%"
    )

    print(
        "Random Forest Failure Probability:",
        round(ml_probability * 100, 2), "%"
    )

    print(
        "Hybrid Failure Probability:",
        round(hybrid_probability * 100, 2), "%"
    )

    prediction = (
        "FAILURE"
        if hybrid_probability >= 0.5
        else "SUCCESS"
    )

    print("\nFinal Prediction:", prediction)


# Test a new build

predict_new_build(
    application="Payment",
    previous_status="FAILURE",
    commits=8,
    changed_files=15,
    previous_failures=2
)


# =====================================================
# END
# =====================================================
