# Türkçe çevrimdışı başlangıç

AptFlow, görevleri açıkça tanımlanmış uzman araçlara bölen bir Python geliştirme iskeletidir. Varsayılan akış **sentetik veri** kullanır; hesap, API anahtarı, Docker, FFmpeg veya harici ağ çağrısı gerekmez. Gerçek NotebookLM, TinyFish, model ve HeyGen adaptörleri henüz uygulanmamıştır.

## Gereksinimler ve ilk çalıştırma

Python 3.11+ ve Git kurulu olmalıdır. Aşağıdaki komutlar Windows üzerinde Python 3.11.9 ile doğrulandı; bu yerel sonuç Linux çalıştırma kanıtı değildir. Windows'ta gerekirse `python` yerine `py -3.11`, Unix'te `python3` kullanın.

```console
git clone https://github.com/Voyagerroc/AptFlow.git
cd AptFlow
python aptflow.py init
python aptflow.py doctor
python aptflow.py plan
python aptflow.py run --out outputs/ilk-demo
```

- `init`, size ait ve Git tarafından yok sayılan `aptflow.json` dosyasını oluşturur. Adaptörleri ve isteğe bağlı belleği bu dosyada kendinize göre düzenleyin.
- `doctor`, seçilen aşamaları ve hazır olma durumunu gösterir. FFmpeg bilgisi yalnızca isteğe bağlı render içindir.
- `plan`, açık rol/adaptör eşleşmesini gösterir; kendiliğinden canlı araç seçmez.
- `run`, yeni çıktı klasöründe `storyboard.json` ve `report.json` oluşturur.

`storyboard.json` sentetik sahne planıdır; üretilmiş avatar videosu değildir. `report.json` içinde `status: demo_completed`, `synthetic: true`, `external_calls: 0` ve `video_generated: false` beklenir. Bu alanlar yalnızca bu demo çalışmasına aittir; gerçek sağlayıcı başarısını veya gelecekteki maliyeti kanıtlamaz.

## Önceki çalışmayı koruma

`init` mevcut yapılandırmanın, `run` mevcut çıktı klasörünün üstüne yazmayı reddeder. Öncekini silmek yerine yeni bir yol seçin:

```console
python aptflow.py init --config config/ikinci-demo.local.json
python aptflow.py doctor --config config/ikinci-demo.local.json
python aptflow.py plan --config config/ikinci-demo.local.json
python aptflow.py run --config config/ikinci-demo.local.json --out outputs/ikinci-demo
```

Aynı örneği tekrar çalıştırırken daha önce kullanılmamış başka bir çıktı adı seçin. Kendi yapılandırma dosyalarınızı ve çıktılarını Git'e eklemeyin.

## Sık karşılaşılan durumlar

| Durum | Yapılacak işlem |
| --- | --- |
| Yapılandırma bulunamadı | Önce `init` çalıştırın veya doğru `--config` yolunu verin. |
| Yapılandırma / çıktı zaten var | Öncekini koruyup yeni bir dosya veya çıktı yolu seçin. |
| API anahtarı ekledim ama canlı işlem yok | Canlı adaptörler henüz uygulanmadı; anahtar eklemek yeterli değildir. |
| `doctor` canlı sağlayıcı için hazır değil | Beklenen sınırdır; [adaptör sözleşmesini](ADAPTERS.md) uygulamak ve test etmek gerekir. |
| FFmpeg / ffprobe bulunamadı | Storyboard demosu için gerekmez; yalnızca isteğe bağlı render için kurun. |
| Video veya ses oluşmadı | Varsayılan akış storyboard üretir; avatar/ses hizmeti çağırmaz. |

## İsteğe bağlı yerel video render

FFmpeg/ffprobe ve izinli bir TrueType fontla yerel başlık kartları render edilebilir; bu, gerçek bir avatar hizmeti değildir. Sürüme uygun seçenekler için `python aptflow.py render --help` ve [komut başvurusundaki](CLI.md) render bölümüne (İngilizce) bakın. FFmpeg render bu başlangıç doğrulamasında çalıştırılmadı.

## Katkı ve doğrulama

```console
python -m unittest discover -s tests -v
```

Yerel Windows/Python 3.11.9 kontrolünde 12 test geçti; farklı bir sürümün sonucu [GitHub Actions kontrollerinde](https://github.com/Voyagerroc/AptFlow/actions/workflows/ci.yml) ayrıca değerlendirilmelidir. Sentetik fixture kullanın; kimlik bilgisi, özel medya veya kişisel notebook kimliği paylaşmayın. [CONTRIBUTING](../CONTRIBUTING.md) ve [güvenlik politikası](../SECURITY.md) kapsamı açıklar.

---

Erol Taşcı, Voyagerroc Technologies · [voyagerroctechnologies.com](https://voyagerroctechnologies.com/)
