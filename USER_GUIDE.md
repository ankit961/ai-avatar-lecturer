# AI Doctor Avatar - User Guide

## 🚀 Quick Start

### 1. Start the System
```bash
cd /Users/ankit_chauhan/Desktop/doctor-avatar
python3 backend/app.py
```

### 2. Open Web Interface
Visit: **http://localhost:9000/ui**

## 📱 Web Interface Guide

### Tab 1: Basic Video Generation
1. **Enter your medical lecture text** (any language)
2. **Select target language** from dropdown
3. **Click "Generate Video"**
4. **Wait for processing** (6-9 seconds)
5. **Download your video** when complete

### Tab 2: Custom Image Video
1. **Upload your own portrait image** (JPG/PNG)
2. **Enter your medical lecture text**
3. **Select target language**
4. **Optionally upload voice reference** for cloning
5. **Click "Generate Video with Custom Image"**
6. **Download when complete**

## 🌍 Supported Languages

| Language | Code | TTS Quality | Translation |
|----------|------|-------------|-------------|
| English  | en   | ⭐⭐⭐⭐⭐    | Native      |
| Hindi    | hi   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Gujarati | gu   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Marathi  | mr   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Tamil    | ta   | ⭐⭐⭐⭐⭐    | ✅ Good      |
| Telugu   | te   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Bengali  | bn   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Kannada  | kn   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Malayalam| ml   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Punjabi  | pa   | ⭐⭐⭐⭐⭐    | ✅ Excellent |
| Urdu     | ur   | ⭐⭐⭐⭐⭐    | ✅ Excellent |

## 💡 Tips for Best Results

### Text Input
- **Medical content works best** (the system is optimized for medical lectures)
- **Keep sentences clear and well-structured**
- **Avoid very long paragraphs** (break into smaller chunks)
- **Use proper punctuation** for natural speech rhythm

### Custom Images
- **Use clear, front-facing portraits** for best results
- **Recommended size**: 512x512 pixels or larger
- **Good lighting** improves video quality
- **Neutral background** works best

### Voice References (Optional)
- **3-10 seconds of clear speech** is ideal
- **Same language as target output** works best
- **Good audio quality** improves cloning results
- **WAV format preferred** but MP3 also works

## 🔧 Troubleshooting

### Common Issues

**"Generation taking too long"**
- Normal processing time: 6-9 seconds
- Complex text may take longer
- Check server logs if > 30 seconds

**"Video quality not as expected"**
- System uses fallback video generation for reliability
- Advanced lip-sync may not always work
- Static video with clear audio is the current output

**"Language not translating properly"**
- Try breaking text into shorter sentences
- Some languages use fallback translation models
- English input generally works best

**"Custom image not working"**
- Ensure image is clear and front-facing
- Try reducing image size if very large
- JPG and PNG formats supported

### Error Messages

**"Translation failed"**
- Try with English input text
- Check if language is supported
- Break complex sentences into simpler ones

**"TTS generation failed"**
- System will automatically try fallback engines
- Refresh and try again
- Check text for special characters

**"Video generation failed"**
- System uses reliable fallback method
- Check that portrait image is valid
- Ensure sufficient disk space

## 📊 Expected Output

### What You'll Get
- **MP4 video file** (70-180KB typical size)
- **Clear audio** in selected language
- **Static portrait** with synchronized audio
- **Professional quality** suitable for educational use

### Processing Time
- **Translation**: 2-3 seconds
- **Speech synthesis**: 1-2 seconds
- **Video creation**: 3-4 seconds
- **Total**: 6-9 seconds average

## 🆘 Getting Help

### Support Resources
1. **Check SYSTEM_STATUS.md** for technical details
2. **Review backend logs** for error details
3. **Test with simple English text** first
4. **Try different browsers** if interface issues

### Contact Information
- **System Status**: Check `/Users/ankit_chauhan/Desktop/doctor-avatar/SYSTEM_STATUS.md`
- **Technical Logs**: Backend console output
- **Test Results**: `/Users/ankit_chauhan/Desktop/doctor-avatar/outputs/`

---

**Enjoy creating your AI-powered medical lectures!** 🎓🤖
