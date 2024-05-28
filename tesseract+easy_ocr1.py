import os,sys
sys.path.insert(0, r'C:\Users\admin\pythonworks')
import numpy as np
from preproces import deskew
import pytesseract
from pytesseract import Output
import re
from pdf2image import convert_from_path
import glob, cv2
import easyocr
import json
import skimage.filters as filters

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'-l rus+kaz+eng --psm 1 --oem 2'  # -c preserve_interword_spaces=1' # --min-conf 50'

reader = easyocr.Reader(['ru'])
def convert_txt(from_path,to_path, ocr):
    all_pdfs = [file_ for file_ in glob.glob(r'%s\*' % from_path) if file_.lower().endswith(".pdf") and "szpo_qr" not in file_]
    directory = os.path.basename(to_path)
    #path = os.path.join(to_path, directory)
    #os.makedirs(path,exist_ok=True)
    txt_file = to_path+'/%s_ocr.json'%directory
    my_dict = {
      'bid': f"{directory}",
      'files': []
    }
    for file_num in range(len(all_pdfs)):
        
        pages = convert_from_path(all_pdfs[file_num], last_page=10, thread_count=4,
                                  poppler_path=r'C:\Users\admin\poppler-0.68.0\bin')
        all_text_tess=[]
        all_text_easy=[]
        for i in range(len(pages)):
            page = pages[i]
            img = np.array(page)
            img = deskew(img)  
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            smooth = cv2.GaussianBlur(gray, (95,95), 0)
            division = cv2.divide(gray, smooth, scale=255)
            result = filters.unsharp_mask(division, radius=1.5, amount=1.5, multichannel=False, preserve_range=False)
            result = (255*result).clip(0,255).astype(np.uint8)
            if "tesseract" in ocr:
                df = pytesseract.image_to_data(result, config=custom_config, output_type=Output.DICT)
                hier = [(p[10], p[11]) for p in zip(*df.values())]
                main_text = ''
                for b in hier:
                    if b[0] == '-1':
                        continue
                    if b[1].replace(" ", "") != '':
                        main_text += ' ' + b[1]
                main_text = re.sub(r'\n+', '\n', main_text).strip()
                main_text = re.sub(r' +', ' ', main_text).strip()
                all_text_tess.append(main_text)
                if len(my_dict['files'])==file_num:
                    my_dict['files'].append({"original_file":os.path.basename(all_pdfs[file_num]),
                                         "ocr_versions":{'tesseract_v1':[{"page":b+1,"text":all_text_tess[b]} for b in range(len(all_text_tess))]}})
                else:
                    my_dict['files'][file_num]['ocr_versions'].update({"tesseract_v1": [{"page":b+1,"text":all_text_tess[b]} for b in range(len(all_text_tess))]})
            if "easyocr" in ocr:
                bounds = reader.readtext(result,detail=0)
                main_text = ''
                for b in bounds:
                  main_text += ' ' + b
                main_text = re.sub(r'\n+', '\n', main_text).strip()
                main_text = re.sub(r' +', ' ', main_text).strip()
                all_text_easy.append(main_text)
                if len(my_dict['files'])==file_num:
                    my_dict['files'].append({"original_file":os.path.basename(all_pdfs[file_num]),
                                         "ocr_versions":{'easyocr_v1':[{"page":b+1,"text":all_text_easy[b]} for b in range(len(all_text_easy))]}})
                else:
                    my_dict['files'][file_num]['ocr_versions'].update({"easyocr_v1": [{"page":b+1,"text":all_text_easy[b]} for b in range(len(all_text_easy))]})
        
    if os.path.exists(txt_file):   
        f = open(txt_file, encoding='utf-8')  
        data = json.load(f)
        for orig in my_dict['files']:
            for d in data['files']:
                if d['original_file'] == orig['original_file']:
                    for version in my_dict['files'][0]['ocr_versions']:
                        d['ocr_versions'][version]=my_dict['files'][0]['ocr_versions'][version] 
        with open(txt_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file,ensure_ascii=False)    
    else:
        with open(txt_file, 'w', encoding='utf-8') as json_file:
            json.dump(my_dict, json_file,ensure_ascii=False)

if __name__ == "__main__":

    convert_txt(r'C:\Users\admin\pythonworks\dataset\10150712\original_files', "C:\\Users\\admin\\pythonworks\\dataset\\10150712", ("tesseract","easyocr"))


import json
  
# Opening JSON file
f = open(r'C:\\Users\\admin\\pythonworks\\dataset\\10150712\\10150712_ocr.json', encoding='utf-8')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
f1 = open(r'C:\\Users\\admin\\pythonworks\\dataset\\10150712\\10150712_ocr.json', encoding='utf-8')
  
# returns JSON object as 
# a dictionary
data1 = json.load(f1)