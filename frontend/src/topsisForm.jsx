import React, { useState } from 'react';
import  axios  from 'axios';

function TopsisForm() {
  const [formData, setFormData] = useState({
    dataFile: null,
    weights: '',
    impact: '',
    emailid: ''
  });

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: files ? files[0] : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Process form data
    const data = new FormData();
    data.append('dataFile', formData.dataFile); // Assuming this is the file input
    data.append('weights', formData.weights);
    data.append('impact', formData.impact);
    data.append('emailid', formData.emailid);

    try {
      const response = await axios.post('http://127.0.0.1:5000/', data);
      if (response.data && response.data.download_url) {
        // Create an invisible anchor element to trigger the download
        const link = document.createElement('a');
        link.href = `${window.location.origin}${response.data.download_url}`;
        // Use the actual filename for the 'download' attribute if you want to specify a name
        link.setAttribute('download', true);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        alert("File processed but no download link returned.");
      }
    } catch (error) {
      console.error('Error:', error.response ? error.response.data : 'Unknown Error');
      alert("An error occurred while submitting the form.");
    }
  };
    


  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" encType="multipart/form-data">
        <h1 className="block text-gray-700 text-xl font-bold mb-4">Topsis</h1>
         
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="dataFile">
            1. Data file (data.csv)
          </label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="file" id="dataFile" name="dataFile" onChange={handleChange} />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="weights">
            2. Weights
          </label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="text" id="weights" name="weights" value={formData.weights} onChange={handleChange} placeholder="Enter weights" />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="impact">
            3. Impact
          </label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="text" id="impact" name="impact" value={formData.impact} onChange={handleChange} placeholder="Enter impact" />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="emailid">
            4. Email ID
          </label>
          <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" type="emailid" id="emailid" name="emailid" value={formData.emailid} onChange={handleChange} placeholder="Enter your email ID" />
        </div>
        <div className="flex items-center justify-between">
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
            Submit
          </button>
        </div>
      </form>
    </div>
  );
}

export default TopsisForm;
