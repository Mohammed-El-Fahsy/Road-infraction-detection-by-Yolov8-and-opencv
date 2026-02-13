import React, { useEffect, useState } from 'react';
import styled from 'styled-components';

const Radio = () => {
  return (
    <StyledWrapper>
      <div>
        <input type="checkbox" id="theme-mode" className="mode" hidden />
        <div className="container">
          <div className="wrap">
            <img src="/image.png" alt="Road Infractions Logo" width="18%" className="image" />
            <input defaultChecked type="radio" id="rd-1" name="radio" className="rd-1" hidden />
            <label htmlFor="rd-1" className="label" style={{zIndex: 1}}><span>All</span></label>
            <input type="radio" id="rd-2" name="radio" className="rd-2" hidden />
            <label htmlFor="rd-2" className="label" style={{zIndex: 2}}><span>Red Light</span></label>
            <input type="radio" id="rd-3" name="radio" className="rd-3" hidden />
            <label htmlFor="rd-3" className="label" style={{zIndex: 3}}><span>Solid Line</span></label>
            <input type="radio" id="rd-4" name="radio" className="rd-4" hidden />
            <label htmlFor="rd-4" className="label" style={{zIndex: 4}}><span>No Entry</span></label>
            <div className="bar" />
            <div className="slidebar" />
          </div>
          
          {/* Render Violations component here */}
          <Violations />
        </div>
        <div className="container2">
          © 2026 Mohammed El Fahsy. All rights reserved.
        </div>
      </div>
    </StyledWrapper>
  );
}

function Violations() {
  const [violations, setViolations] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    fetch("http://localhost/get.php")
      .then((res) => res.json())
      .then((data) => setViolations(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <>
      <div className="cards-container">
      {/* En-têtes une seule fois */}
      <div className="card-header">
        <div className="card__data">
          <div className="card__right">
            <div className="card__title">Time</div>
          </div>
          <div className="card__right">
            <div className="card__title">Date</div>
          </div>
          <div className="card__right">
            <div className="card__title">Location</div>
          </div>
          <div className="card__right">
            <div className="card__title">Type</div>
          </div>
          <div className="card__right">
            <div className="card__title">Traffic fine</div>
          </div>
          <div className="card__right">
            <div className="card__title">Vehicle</div>
          </div>
        </div>
      </div>
      
      {/* Données des violations */}
      {violations.map((v, index) => (
        <div className="card" key={index}>
          <div className="card__data">
            <div className="card__right">
              <div className="item">{v.temps}</div>
            </div>
            <div className="card__right">
              <div className="item">{v.date}</div>
            </div>
            <div className="card__right">
              <div className="item">{v.lieu}</div>
            </div>
            <div className="card__right">
              <div className="item">{v.type}</div>
            </div>
            <div className="card__right">
              <div className="item">{v.prix} DH</div>
            </div>
            <div className="card__right">
             <button 
                    className="view-image-btn"
                    onClick={() => setSelectedImage(`http://localhost/${v.photo}`)}
                  >
                    View Image
                  </button>
            </div>
          </div>
        </div>
      ))}
    </div>
    {selectedImage && (
        <ImageModal onClick={() => setSelectedImage(null)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={() => setSelectedImage(null)}>
              &times;
            </CloseButton>
            <EnlargedImage src={selectedImage} alt="Agrandie" />
          </ModalContent>
        </ImageModal>
      )}
    </>
  );
}

// Ajoutez ces composants styled à la fin de votre StyledWrapper
const ImageModal = styled.div`
 border: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  cursor: pointer;
`;

const ModalContent = styled.div`
  position: relative;
  max-width: 90%;
  max-height: 90%;
  cursor: default;
`;

const CloseButton = styled.button`
  position: absolute;
  top: -40px;
  right: -10px;
  background: none;
  border: none;
  color: white;
  font-size: 40px;
  cursor: pointer;
  z-index: 1001;
  
  &:hover {
    color: #ff4444;
  }
`;

const EnlargedImage = styled.img`
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
`;

const StyledWrapper = styled.div`
  /* theme-mode-style */
  .mode + .container {
    --color-pure: #000;
    --color-primary: #e8e8e8;
    --color-secondary: #212121;
    --muted: #b8b8b8;
  }
  .mode:checked + .container {
    --color-pure: #fff;
    --color-primary: ##212121;
    --color-secondary: #fff;
    --muted: #383838;
  }
  .container {
    background-color: var(--color-secondary);
    position: fixed;
    width: 100%;
    height: 110%;
    display: flex;
   
    flex-direction: column;
  }
    .container2 {
     font-weight: 500;
    font-size:16px;
    color:#212121;
     padding: 6px 0px;
     width: 100%;
    background-color: #e8e8e8;
    position: fixed;
    display: flex;
    bottom:0px;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
  .container .theme {
    color: var(--color-secondary);
    background-color: var(--color-primary);
    position: relative;
    cursor: pointer;
    z-index: 9;
    -webkit-user-select: none;
    user-select: none;
    border: 1px solid var(--muted);
    border-radius: calc(var(--round) - var(--p-y));
    margin-left: calc(var(--p-x) * 2);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px;
    transition: background-color 0.25s linear;
  }
    .view-image-btn{
    padding: 1px 75.8px;}
  .container .theme:hover {
    background-color: var(--muted);
  }
  .image{
  margin-right:550px;
   padding: -5px -5px ;}
  .container .theme::before {
    content: "";
    position: absolute;
    left: calc(var(--p-x) * -1);
    width: 90%;
    height: 80%;
    background-color: var(--muted);
  }
  .container .theme span {
    border: none;
    outline: none;
    background-color: transparent;
    padding: 0.125rem;
    border-radius: 9999px;
    align-items: center;
    justify-content: center;
  }
  .mode:checked + .container .theme span.light,
  .mode + .container .theme span.dark {
    display: none;
  }
  .mode + .container .theme span.light,
  .mode:checked + .container .theme span.dark {
    display: flex;
  }
  .container .theme svg {
    stroke-linejoin: round;
    stroke-linecap: round;
    stroke: currentColor;
    fill: none;
    height: 22px;
    width: 22px;
  }

  /* main style */
  .wrap {
    
    --p-x: 8px;
    --p-y: 4px;
    --w-label: 100px;
    display: flex;
    align-items: center;
    padding: var(--p-y) var(--p-x);
    position: relative;
    background: var(--color-primary);
    border-radius: var(--round);
    max-width: 100%;
    overflow-x: auto;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    top: 0;
    z-index: 1;
  }

  .wrap input {
    height: 0;
    width: 0;
    position: absolute;
    overflow: hidden;
    display: none;
    visibility: hidden;
  }

  .label {
    cursor: pointer;
    outline: none;
    font-size: 0.875rem;
    letter-spacing: initial;
    font-weight: 500;
    color: var(--color-secondary);
    background: transparent;
    padding: 2px 1px;
    width: var(--w-label);
    min-width: var(--w-label);
    text-decoration: none;
    -webkit-user-select: none;
    user-select: none;
    transition: color 0.25s ease;
    outline-offset: -6px;
    display: flex;
      justify-content: center;
  
    position: relative;
    z-index: 2;
    -webkit-tap-highlight-color: transparent;
  }
  .label span {
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 1;
  }

  .wrap input[class*="rd-"]:checked + label {
    color: var(--color-pure);
  }

  .bar {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    position: absolute;
    transform-origin: 0 0 0;
    height: 100%;
    width: var(--w-label);
    z-index: 0;
    transition: transform 0.5s cubic-bezier(0.33, 0.83, 0.99, 0.98);
  }
  .bar::before,
  .bar::after {
    content: "";
    position: absolute;
    height: 4px;
    width: 100%;
    background: var(--color-secondary);
  }
  .bar::before {
    top: 0;
    border-radius: 0 0 9999px 9999px;
  }
  .bar::after {
    bottom: 0;
    border-radius: 9999px 9999px 0 0;
  }

  .slidebar {
    position: absolute;
    height: calc(100% - (var(--p-y) * 4));
    width: var(--w-label);
    border-radius: calc(var(--round) - var(--p-y));
    background: var(--muted);
    transform-origin: 0 0 0;
    z-index: 0;
    transition: transform 0.5s cubic-bezier(0.33, 0.83, 0.99, 0.98);
  }

  .rd-1:checked ~ .bar,
  .rd-1:checked ~ .slidebar,
  .rd-1 + label:hover ~ .slidebar {
    transform: translateX(800%) scaleX(1);
  }
  .rd-2:checked ~ .bar,
  .rd-2:checked ~ .slidebar,
  .rd-2 + label:hover ~ .slidebar {
    transform: translateX(900%) scaleX(1);
  }
  .rd-3:checked ~ .bar,
  .rd-3:checked ~ .slidebar,
  .rd-3 + label:hover ~ .slidebar {
    transform: translateX(1000%) scaleX(1);
  }
    .rd-4:checked ~ .bar,
  .rd-4:checked ~ .slidebar,
  .rd-4 + label:hover ~ .slidebar {
    transform: translateX(1100%) scaleX(1);
  }
     .rd-5:checked ~ .bar,
  .rd-5:checked ~ .slidebar,
  .rd-5 + label:hover ~ .slidebar {
    transform: translateX(1115%) scaleX(1);
  }
    .card {
    position: relative;
   
    width: 100%;
    background: rgb(44, 44, 44);
    font-family: "Courier New", Courier, monospace;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    overflow: hidden;
    z-index: 900;
  }

  .card__title {
    color: white;
    font-weight: bold;
    padding: 13px 10px;
    border-bottom: 1px solid rgb(167, 159, 159);
    font-size: 0.95rem;
  }

  .card__data {
    font-size: 0.8rem;
    display: flex;
    justify-content: space-between;
    border-right: 1px solid rgb(203, 203, 203);
    border-left: 1px solid rgb(203, 203, 203);
    border-bottom: 1px solid rgb(203, 203, 203);
  }

  .card__right {
    width: 60%;
    border-right: 1px solid rgb(203, 203, 203);
  }

  .card__left {
    width: 40%;
    text-align: end;
  }

  .item {
    padding: 3px 0;
    background-color: white;
  }

  .card__right .item {
    padding-left: 0.8em;
  }

  .card__left .item {
    padding-right: 0.8em;
  }

  .item:nth-child(even) {
    background: rgb(234, 235, 234);}`;

export default Radio ;

