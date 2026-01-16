// Form field configuration
// This file can be easily replaced to modify form fields without changing the main HTML file

const formFields = {
    age: {
        keywords: ['age', 'years old', 'please tell me your age'],
        type: 'number',
        placeholder: 'Enter your age',
        label: 'Age',
        min: 10,
        max: 100
    },
    gender: {
        keywords: ['gender', 'male', 'female', 'please tell me your gender'],
        type: 'radio',
        options: [
            { value: 'male', label: 'Male' },
            { value: 'female', label: 'Female' }
        ],
        label: 'Gender'
    },
    weight: {
        keywords: ['weight', 'kg', 'kilogram', 'please tell me your weight'],
        type: 'number',
        placeholder: 'Enter your weight (kg)',
        label: 'Weight (kg)',
        min: 30,
        max: 200
    },
    height: {
        keywords: ['height', 'cm', 'centimeter', 'please tell me your height'],
        type: 'number',
        placeholder: 'Enter your height (cm)',
        label: 'Height (cm)',
        min: 100,
        max: 250
    },
    injuries: {
        keywords: ['injuries', 'injury', 'past year', 'knees', 'ankles', 'back', 'any injuries'],
        type: 'text',
        placeholder: 'Describe any injuries in the past year (especially knees, ankles, or back)',
        label: 'Injuries in the Past Year'
    },
    fitness_level: {
        keywords: ['fitness level', 'current fitness', 'fitness', 'level'],
        type: 'select',
        options: [
            { value: 'beginner', label: 'Beginner' },
            { value: 'intermediate', label: 'Intermediate' },
            { value: 'advanced', label: 'Advanced' }
        ],
        label: 'Current Fitness Level'
    },
    running_times_per_week: {
        keywords: ['run per week', 'running times', 'times per week', 'how many times do you run', 'running frequency'],
        type: 'number',
        placeholder: 'Enter number of times per week',
        label: 'Running Times Per Week',
        min: 0,
        max: 7
    },
    total_mileage: {
        keywords: ['mileage', 'total mileage', 'total km', 'weekly mileage', 'average mileage'],
        type: 'number',
        placeholder: 'Enter total mileage per week (km)',
        label: 'Total Mileage Per Week (km)',
        min: 0,
        max: 200
    },
    pb: {
        keywords: ['pb', 'personal best', '5km', '10km', '5km or 10km', 'best time'],
        type: 'text',
        placeholder: 'Your PB for 5km or 10km run (e.g., 5km: 25:00)',
        label: 'PB for 5km or 10km Run'
    },
    training_goal: {
        keywords: ['training goal', 'goal', 'weight loss', 'stay fit', '10km race', 'half-marathon', 'full marathon'],
        type: 'checkbox',
        options: [
            { value: 'weight loss', label: 'Weight Loss' },
            { value: 'stay fit', label: 'Stay Fit' },
            { value: 'train for 10km race', label: 'Train for a 10km Race' },
            { value: 'train for half-marathon', label: 'Train for a Half-Marathon' },
            { value: 'train for full marathon', label: 'Train for a Full Marathon' }
        ],
        label: 'Training Goal (Multiple Selection)'
    },
    training_days: {
        keywords: ['days of the week', 'training days', 'which days', 'how long each session', 'training schedule'],
        type: 'text',
        placeholder: 'Which days can you train and for how long each session (e.g., Monday/Wednesday/Friday, 1 hour)',
        label: 'Training Days & Session Duration'
    },
    training_location: {
        keywords: ['where do you train', 'training location', 'road', 'track', 'treadmill', 'trail', 'where do you usually train'],
        type: 'select',
        options: [
            { value: 'road', label: 'Road' },
            { value: 'track', label: 'Track' },
            { value: 'treadmill', label: 'Treadmill' },
            { value: 'trail', label: 'Trail' }
        ],
        label: 'Training Location'
    },
    arch_type: {
        keywords: ['arches', 'arch', 'low', 'flat', 'neutral', 'high arches', 'shoe finder'],
        type: 'select',
        options: [
            { value: 'low (flat)', label: 'Low (Flat)' },
            { value: 'neutral', label: 'Neutral' },
            { value: 'high', label: 'High' }
        ],
        label: 'Arch Type (Shoe Finder)'
    },
    shoe_wear: {
        keywords: ['wear', 'old shoes', 'inner edge', 'outer edge', 'shoe wear pattern'],
        type: 'select',
        options: [
            { value: 'inner edge', label: 'Inner Edge' },
            { value: 'outer edge', label: 'Outer Edge' },
            { value: 'even', label: 'Even Wear' }
        ],
        label: 'Shoe Wear Pattern'
    },
    shoe_feel: {
        keywords: ['soft', 'plush', 'firm', 'responsive', 'ride', 'shoe feel', 'prefer'],
        type: 'select',
        options: [
            { value: 'soft, plush feel', label: 'Soft, Plush Feel' },
            { value: 'firm, responsive ride', label: 'Firm, Responsive Ride' }
        ],
        label: 'Shoe Feel Preference'
    },
    city: {
        keywords: ['city', 'area', 'location', 'place', 'where', 'what city', 'what city or area are you located in'],
        type: 'text',
        placeholder: 'Enter your city',
        label: 'Location (City)'
    }
};
