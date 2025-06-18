import re, json, os, base64

def encode_image_base64(img_path):
    with open(img_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_text(filepath):
    with open(filepath, 'r', encoding='gb2312') as f:
        return f.read()

def extract_blocks(text, image_dir):
    parts = re.split(r'# 玉米田杂草防除技术', text)
    pest_part = parts[0]
    weed_part = parts[1] if len(parts) > 1 else ""

    pest_sections = re.split(r'###\s+', pest_part)[1:]
    pest_data = []
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for section in pest_sections:
        lines = section.split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:])

        symptoms = re.search(r'\*\*(症状|形态|形态特征)\*\*：(.*?)(\*\*|$)', content, re.S)
        symptom_field, symptom_content = (symptoms.group(1).strip(), symptoms.group(2).strip()) if symptoms else ("", "")
        rules = re.search(r'\*\*(发病规律|发生规律|生活习性)\*\*：(.*?)(\*\*|$)', content, re.S)
        rule_field, rule_content = (rules.group(1).strip(), rules.group(2).strip()) if rules else ("", "")
        controls = re.search(r'\*\*(药剂防治|防治措施|防治方法)\*\*：(.*?)(\*\*|$)', content, re.S)
        control_field, control_content = (controls.group(1).strip(), controls.group(2).strip()) if controls else ("", "")

        matched_imgs = [img for img in image_files if title in img]
        images_info = []
        for imgfile in matched_imgs:
            img_path = os.path.join(image_dir, imgfile)
            if os.path.exists(img_path):
                img_b64 = encode_image_base64(img_path)
                images_info.append({
                    'filename': os.path.splitext(imgfile)[0],  # 去除扩展名
                    'base64': img_b64
                })

        record = {
            "title": title,
            "type": "病虫害",
            "symptom_field": symptom_field,
            "symptom_content": symptom_content,
            "rule_field": rule_field,
            "rule_content": rule_content,
            "control_field": control_field,
            "control_content": control_content,
            "images": images_info
        }
        pest_data.append(record)

    weed_record = {
        "title": "玉米田杂草防除技术",
        "type": "杂草防除",
        "content": weed_part.strip(),
        "images": []
    }

    pest_used_imgs = {img['filename'] for record in pest_data for img in record['images']}
    remaining_imgs = [img for img in image_files if os.path.splitext(img)[0] not in pest_used_imgs]

    for imgfile in remaining_imgs:
        img_path = os.path.join(image_dir, imgfile)
        if os.path.exists(img_path):
            img_b64 = encode_image_base64(img_path)
            weed_record['images'].append({
                'filename': os.path.splitext(imgfile)[0],  # 去除扩展名
                'base64': img_b64
            })

    return pest_data, weed_record

if __name__ == "__main__":
    text = load_text('data/corn_diseases_pests_weeds.txt')
    pest_data, weed_record = extract_blocks(text, 'data/images/')

    with open("data/structured_data.json", "w", encoding="utf-8") as f:
        json.dump({"pests": pest_data, "weed": weed_record}, f, ensure_ascii=False, indent=2)

    print("✅ 数据抽取 + 图片Base64编码 完成！")