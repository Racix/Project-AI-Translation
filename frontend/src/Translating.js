import React, {} from 'react';
import "./styles/TranscriptionDisplay.css";
import "./styles/loading.css";

const Translating = () => {
  return (
    <div>
      <div className="Display">
      <div style={{ display: 'flex', alignItems: 'center' }}>
            <h2 style={{ marginBottom: '25px' }}>translation in progress</h2>
      <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
      </div>
      </div>
    </div>
  );
};

export default Translating;